import requests
from flask import current_app
from config import settings

def suggest_company_by_inn(query: str) -> dict | None:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {settings.dadata_token}"
    }
    body = {"query": query}
    response = requests.post(
        settings.dadata_api_url,
        headers=headers,
        json=body
    )
    if response.status_code != 200:
        return None
    suggestions = response.json().get("suggestions", [])
    return suggestions[0]["data"] if suggestions else None
