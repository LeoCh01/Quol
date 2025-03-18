import asyncio
import ollama
from res.paths import IMG_PATH


async def chat():
    client = ollama.AsyncClient(host='http://localhost:11434')
    print('connected')

    response = await client.chat(
        model='gemma3',
        stream=True,
        messages=[{
            'role': 'user',
            'content': 'give me a brief description of this image',
            'images': [IMG_PATH + 'screenshot.png']
        }]
    )

    async for chunk in response:
        print(chunk['message']['content'], end='', flush=True)


asyncio.run(chat())