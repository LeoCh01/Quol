import io
import shutil
import zipfile
import httpx
import os

from qlib.io_helpers import read_json, write_json

BRANCH = 'main'


def check_for_update() -> tuple:  # is_new_version, new, old
    try:
        settings = read_json(os.getcwd() + '/settings.json')
        if not settings.get('show_updates', True):
            return '', ''

        response = httpx.get(f'https://raw.githubusercontent.com/LeoCh01/Quol/{BRANCH}/app/settings.json')
        response.raise_for_status()
        data = response.json()

        return settings['version'] == data['version'], data['version'], settings['version']

    except Exception as e:
        print(f'Update check failed: {e}')
        return '', '', ''


async def download_minor(item: str) -> bool:
    raw_url = f"https://raw.githubusercontent.com/LeoCh01/Quol/{BRANCH}/modules/{item}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            zip_file = io.BytesIO(response.content)

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(os.getcwd())

        print(f'Successfully extracted {item} to {os.getcwd()}')
        return True

    except httpx.RequestError as e:
        print(f"Error downloading the file: {e}")
        return False
    except zipfile.BadZipFile as e:
        print(f"Error: Invalid zip file: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


async def update_minor() -> bool:
    settings = read_json(os.getcwd() + '/settings.json')

    try:
        response = httpx.get(f'https://raw.githubusercontent.com/LeoCh01/Quol/{BRANCH}/app/settings.json')
        response.raise_for_status()
        settings_new = response.json()
    except Exception as e:
        print(f"Failed to fetch settings: {e}")
        return False

    for k, v in settings_new['packages']['versions'].items():
        if settings['packages']['versions'].get(k, 0) == v:
            continue

        item_path = f'{os.getcwd()}/{k}'

        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

            await download_minor(f'{k}-v{settings_new["packages"]["versions"][k]}.zip')

        except Exception as e:
            print(f"Error updating {item_path}: {e}")
            return False

    try:
        settings['packages']['versions'] = settings_new['packages']['versions']
        write_json(os.getcwd() + '/settings.json', settings)
    except Exception as e:
        print(f"Error updating settings: {e}")
        return False

    return True
