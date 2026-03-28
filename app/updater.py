import io
import shutil
import zipfile
import httpx
import os
import logging

from globals import BASE_DIR
from qlib.io_helpers import read_json, write_json

logger = logging.getLogger(__name__)

BRANCH = 'main'


async def check_for_update() -> tuple:  # is_new_version, new, old
    try:
        settings = read_json(os.path.join(BASE_DIR, 'settings.json'))
        if not settings.get('show_updates', True):
            return '', '', ''

        async with httpx.AsyncClient() as client:
            response = await client.get(f'https://raw.githubusercontent.com/LeoCh01/Quol/{BRANCH}/app/settings.json')
            response.raise_for_status()
            data = response.json()

        return settings['version'] != data['version'], data['version'], settings['version']

    except Exception as e:
        logger.error('Update check failed: %s', e)
        return '', '', ''


async def download_minor(item: str) -> bool:
    raw_url = f"https://raw.githubusercontent.com/LeoCh01/Quol/{BRANCH}/packages/{item}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            zip_file = io.BytesIO(response.content)

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(BASE_DIR)

        logger.info('Successfully extracted %s to %s', item, BASE_DIR)
        return True

    except httpx.RequestError as e:
        logger.error('Error downloading the file: %s', e)
        return False
    except zipfile.BadZipFile as e:
        logger.error('Error: Invalid zip file: %s', e)
        return False
    except Exception as e:
        logger.error('An unexpected error occurred: %s', e)
        return False


async def update_minor() -> bool:
    settings = read_json(os.path.join(BASE_DIR, 'settings.json'))

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'https://raw.githubusercontent.com/LeoCh01/Quol/{BRANCH}/app/settings.json')
            response.raise_for_status()
            settings_new = response.json()
    except Exception as e:
        logger.error('Failed to fetch settings: %s', e)
        return False

    if settings.get('package_version') == settings_new.get('package_version'):
        logger.info('Package version is already up to date')
        settings['version'] = settings_new['version']
        return True

    # Rename packages to temp names for error handling
    temp_renames = {}
    packages = settings_new.get('packages', [])
    
    try:
        for package in packages:
            package_path = os.path.join(BASE_DIR, package)
            
            if os.path.exists(package_path):
                temp_path = package_path + '__temp'
                shutil.move(package_path, temp_path)
                temp_renames[package] = temp_path

        # Download main package
        try:
            await download_minor(f'pkg--v{settings_new["package_version"]}.zip')

            # Remove temp files if download was successful
            for package, temp_path in temp_renames.items():
                try:
                    if os.path.isdir(temp_path):
                        shutil.rmtree(temp_path)
                    else:
                        os.remove(temp_path)
                except Exception as e:
                    logger.error('Error removing temp file %s: %s', temp_path, e)

        except Exception as e:
            logger.error('Error downloading main package: %s', e)
            # Restore from temp files
            for package, temp_path in temp_renames.items():
                try:
                    package_path = os.path.join(BASE_DIR, package)
                    if os.path.exists(temp_path):
                        shutil.move(temp_path, package_path)
                except Exception as restore_err:
                    logger.error('Error restoring %s: %s', package, restore_err)
            return False

    except Exception as e:
        logger.error('Error during update process: %s', e)
        # Restore from temp files
        for package, temp_path in temp_renames.items():
            try:
                package_path = os.path.join(BASE_DIR, package)
                if os.path.exists(temp_path):
                    shutil.move(temp_path, package_path)
            except Exception as restore_err:
                logger.error('Error restoring %s: %s', package, restore_err)
        return False

    try:
        print('Update successful. Cleaning up and updating settings...')
        settings['package_version'] = settings_new['package_version']
        settings['packages'] = settings_new['packages']
        settings['version'] = settings_new['version']
        print('New version:', settings_new['version'])
        write_json(os.path.join(BASE_DIR, 'settings.json'), settings)
    except Exception as e:
        logger.error('Error updating settings: %s', e)
        return False

    return True
