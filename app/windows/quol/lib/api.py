import httpx
import asyncio
from typing import List, Dict, Optional


async def fetch_store_items() -> Optional[List[Dict]]:
    # return [
    #     {'name': 'chance-v1.zip'},
    #     {'name': 'chatgpt.zip'},
    #     {'name': 'chess.zip'},
    #     {'name': 'discord.zip'},
    #     {'name': 'filemanager.zip'},
    #     {'name': 'github.zip'},
    #     {'name': 'google-translate.zip'},
    #     {'name': 'image-editor.zip'},
    #     {'name': 'image-to-text.zip'},
    #     {'name': 'music-player.zip'},
    #     {'name': 'pdf-reader.zip'},
    #     {'name': 'screenshot-tool.zip'},
    #     {'name': 'text-to-speech.zip'},
    #     {'name': 'translator.zip'}
    # ]

    url = "https://api.github.com/repos/LeoCh01/Quol-Tools/contents/tools?ref=main"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Async fetch failed: {e}")
        return None
