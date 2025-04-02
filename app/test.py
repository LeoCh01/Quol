import re

import requests
import json
import os

API_KEY = ''
MODEL_NAME = "gemini-2.0-flash" # Or your preferred model
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

headers = {
    'Content-Type': 'application/json'
}

data = {
  "contents": [
    {
      "role": "user",
      "parts": [
        {"text": "Write a poem about the moon."}
      ]
    }
  ]
  # Optional: "generationConfig": {...}
}

# Use stream=True to enable streaming
response = requests.post(API_URL, headers=headers, json=data).json()
chunks = re.split(r'(\s+)', response['candidates'][0]['content']['parts'][0]['text'])
for chunk in chunks:
    print(chunk, end='')
