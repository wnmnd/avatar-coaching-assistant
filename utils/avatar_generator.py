import requests
from config import D_ID_API_KEY

def generate_avatar_video(text: str) -> str:
    url = "https://api.d-id.com/talks"
    payload = {
        "script": {
            "type": "text",
            "input": text,
        },
        "source_url": "https://create-images-results.d-id.com/DefaultAvatar.jpg"  # default avatar
    }
    headers = {
        "Authorization": f"Basic {D_ID_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    return result.get("result_url")  # Video URL
