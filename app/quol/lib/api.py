import logging
import shutil
import httpx
import zipfile
import io
import os
from typing import List, Dict, Optional

from globals import BASE_DIR
from qlib.io_helpers import read_json

logger = logging.getLogger(__name__)
BASE_URL = 'https://leo-s-website-backend-695678049922.northamerica-northeast2.run.app/quol'
BRANCH = 'main'


async def get_store_items() -> Optional[List[Dict]]:
    url = f"https://api.github.com/repos/LeoCh01/Quol-Tools/contents/tools?ref={BRANCH}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Async fetch failed: {e}")
        return None


async def download_item(item_name: str, path: str) -> bool:
    raw_url = f"https://raw.githubusercontent.com/LeoCh01/Quol-Tools/{BRANCH}/tools/{item_name}.zip"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            zip_file = io.BytesIO(response.content)

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(path)

        logger.info('Successfully extracted %s to %s', item_name, path)
        return True

    except httpx.RequestError as e:
        logger.error(f"Error downloading the file: {e}")
        return False
    except zipfile.BadZipFile as e:
        logger.error(f"Error: Invalid zip file: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False


def is_compatible(version: str) -> bool:
    def v_to_int(v: str):
        parts = v.lstrip('v').split('.')
        while len(parts) < 3:
            parts.append('0')
        return int(parts[0]) * 1000000 + int(parts[1]) * 1000 + int(parts[2])

    settings = read_json(os.path.join(BASE_DIR, 'settings.json'))
    return version == "x" or v_to_int(version) <= v_to_int(settings['version'])


async def update_item(item_name: str, item_ver: int, path: str) -> bool:
    item_path = os.path.join(path, item_name)
    backup_path = os.path.join(path, f"{item_name}_backup")

    try:
        # Rename old item to backup
        if os.path.exists(item_path):
            os.rename(item_path, backup_path)

        # Download new item
        is_downloaded = await download_item(f'{item_name}--v{item_ver}', path)

        if not is_downloaded:
            # Restore backup if download failed
            if os.path.exists(backup_path):
                os.rename(backup_path, item_path)
            return False

        # Check compatibility
        if os.path.exists(os.path.join(item_path, 'res', 'config.json')):
            config = read_json(os.path.join(item_path, 'res', 'config.json'))
            v = config['_'].get('dependency', 'x')
            if not is_compatible(v):
                logger.error(f"Item {item_name} requires app version {v} or higher.")
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                # Restore backup
                if os.path.exists(backup_path):
                    os.rename(backup_path, item_path)
                return False

        # Remove backup if everything succeeded
        if os.path.exists(backup_path):
            if os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
            else:
                os.remove(backup_path)

        return True

    except Exception as e:
        logging.error(f"Error updating {item_name}: {e}")
        # Restore backup on any error
        if os.path.exists(backup_path):
            os.rename(backup_path, item_path)
        return False


async def fetch_notes():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f'{BASE_URL}/notes')
        r.raise_for_status()
        return r.text


async def post_notes(admin_key, notes):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f'{BASE_URL}/notes/{admin_key}',
            json={"notes": notes}
        )
        r.raise_for_status()
        return True
