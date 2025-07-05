import secrets
from datetime import datetime, timedelta

import jwt

from config import settings
from src import db
from src.db.models import RefreshToken


def generate_access_token(user_id: int) -> str:
    payload = {
        'exp': datetime.now() + timedelta(minutes=settings.expire_access_token_time),
        'iat': datetime.now(),
        'sub': str(user_id),
        'type': 'access'
    }
    return jwt.encode(payload, settings.secret_key, algorithm='HS256')

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
        payload = jwt.decode(token, settings.secret_key, algorithms=['HS256'])
        if payload.get('type') != 'access':
            raise Exception('Неверный тип токена')
        return payload['user_id']
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



def create_refresh_token(user_id: int) -> str:
    token = secrets.token_urlsafe(64)
    expires = datetime.now() + timedelta(days=settings.expire_refresh_token_days)

    # Здесь нужно сохранить токен в БД:
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires
    )
    db.session.add(refresh_token)
    db.session.commit()

    return token
