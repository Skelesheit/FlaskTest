from datetime import datetime, timedelta, timezone

import jwt

from config import settings


def generate_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        'exp': now + timedelta(minutes=settings.expire_access_token_time),
        'iat': now,
        'sub': str(user_id),
        'type': 'access'
    }
    secret_key = settings.secret_key
    print("secret on generate:", secret_key)
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    print("token by generate:", token)
    return token


def generate_email_token(user_id: int) -> str:
    payload = {
        'exp': datetime.now() + timedelta(minutes=settings.expire_access_token_time),
        'iat': datetime.now(),
        'sub': 'email_verification',
        'user_id': str(user_id),
    }
    return jwt.encode(payload, settings.mail_secret, algorithm='HS256')


def validate_token(token: str) -> int | None:
    try:
        secret_key = settings.secret_key
        print("secret on validate:", secret_key)
        print(f"settings.secret_key = {settings.secret_key!r}")
        print("token by validate:", token)
        print(f"Token raw: {repr(token)}")
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
            options={"require": ["exp", "iat", "sub", "type"]},
            leeway=10
        )

        if payload.get('type') != 'access':
            raise Exception('Неверный тип токена')
        return int(payload['sub'])
    except jwt.ExpiredSignatureError:
        raise Exception('Токен истёк')
    except jwt.InvalidTokenError:
        raise Exception('Неверный токен')


def decode_email_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.mail_secret, algorithms=["HS256"])
        if payload.get("sub") != "email_verification":
            return None
        return int(payload.get("user_id"))
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
