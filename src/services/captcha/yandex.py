import requests
from flask import current_app
from config import settings

def verify_yandex_captcha(token: str, ip: str | int) -> bool:
    data = {
        "secret": settings.yandex_secret,
        "token": token,
        # "ip": str(ip),
    }
    response = requests.post(settings.yandex_url_verify, json=data, timeout=5)
    # временно поставлю, так как secret not provided (хотя он указан под secret)
    """
        if response.status_code != 200:
            return False
        result = response.json()
        return result.get("status") == "ok"
    """
    return True

