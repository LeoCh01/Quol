import io
import shutil
import zipfile
import httpx
import requests
import os

from qlib.io_helpers import read_json, write_json

BRANCH = 'main'


def check_for_update() -> tuple:  # is_new_verion, new, old 
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

def on_dont_show_changed(state):
    settings = read_json(os.getcwd() + '/settings.json')
    settings['show_updates'] = (state != 2)
    write_json(os.getcwd() + '/settings.json', settings)


async def download_patch(item: str, is_pkg=False) -> bool:
    raw_url = f"https://raw.githubusercontent.com/LeoCh01/Quol/{BRANCH}/modules/{item}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            zip_file = io.BytesIO(response.content)

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(f'{os.getcwd()}/{"_internal" if is_pkg else ""}')

        print(f'Successfully extracted {item} to {os.getcwd()}/{"_internal" if is_pkg else ""}')
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


async def update_patch(version) -> bool:
    manifest = read_json(os.getcwd() + '/manifest.json')

    try:
        response = requests.get(f'https://raw.githubusercontent.com/LeoCh01/Quol/{BRANCH}/app/manifest.json')
        response.raise_for_status()
        manifest_new = response.json()
    except Exception as e:
        print(f"Failed to fetch manifest: {e}")
        return False

    for k, v in manifest_new['versions'].items():
        if manifest['versions'].get(k, v) == v:
            continue

        item_path = f'{os.getcwd()}/' + (f'_internal/{k[1:]}' if k[0] == '*' else k)

        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

            await download_patch(f'{k[1:] if k[0] == "*" else k}-v{manifest_new["versions"][k]}.zip', k[0] == '*')

        except Exception as e:
            print(f"Error updating {item_path}: {e}")
            return False

    try:
        write_json(os.getcwd() + '/manifest.json', manifest_new)

        settings = read_json(os.getcwd() + '/settings.json')
        settings['version'] = version
        write_json(os.getcwd() + '/settings.json', settings)
    except Exception as e:
        print(f"Error updating manifest and settings: {e}")
        return False

    return True