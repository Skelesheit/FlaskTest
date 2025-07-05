import requests
from flask import current_app
from config import settings

def verify_yandex_captcha(token: str, ip: str | None = None) -> bool:
    secret = settings.yandex_secret
    data = {
        "secret": secret,
        "token": token,
    }
    if ip:
        data["ip"] = ip

    response = requests.post(settings.yandex_url_verify, json=data)
    if response.status_code != 200:
        return False

    result = response.json()
    return result.get("status") == "ok"
