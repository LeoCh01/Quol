import io
import os
import zipfile

import httpx


async def download_item(item: str) -> bool:
    raw_url = f"https://raw.githubusercontent.com/LeoCh01/Quol/main/app/{item}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            zip_file = io.BytesIO(response.content)

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(os.getcwd())

        print(f"Successfully extracted {item}")
        return True

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

download_item('res')