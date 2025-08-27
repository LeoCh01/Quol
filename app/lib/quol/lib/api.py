import shutil
import httpx
import zipfile
import io
import os
from typing import List, Dict, Optional


async def get_store_items() -> Optional[List[Dict]]:
    url = "https://api.github.com/repos/LeoCh01/Quol-Tools/contents/tools?ref=main"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Async fetch failed: {e}")
        return None


async def download_item(item_name: str, path: str) -> bool:
    raw_url = f"https://raw.githubusercontent.com/LeoCh01/Quol-Tools/main/tools/{item_name}.zip"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            zip_file = io.BytesIO(response.content)

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(path)

        print(f"Successfully extracted {item_name} to {path}")
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


async def update_item(new_item_name: str, old_item_name: str, path: str) -> bool:
    old_item_path = os.path.join(path, old_item_name)

    try:
        if os.path.exists(old_item_path):
            if os.path.isdir(old_item_path):
                shutil.rmtree(old_item_path)
            else:
                os.remove(old_item_path)

        return await download_item(new_item_name, path)

    except Exception as e:
        print(f"Error updating {old_item_name} to {new_item_name}: {e}")
        return False
