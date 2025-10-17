import requests
import os
from dotenv import load_dotenv


def fetch_html(target_url : str): 

    url = "https://api.firecrawl.dev/v2/scrape"

    payload = {
    "url": target_url,
    "onlyMainContent": False,
    "maxAge": 172800000,
    "parsers": [
        "pdf"
    ],
    "formats": [
        "html"
    ]
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('FIRECRAWL_API_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    return data["data"]["html"]