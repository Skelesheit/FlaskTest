import secrets
from datetime import datetime, timedelta

import jwt

from config import settings
from src import db
from src.db.models import RefreshToken


def generate_access_token(user_id) -> str:
    payload = {
        'exp': datetime.now() + timedelta(minutes=settings.expire_access_token_time),
        'iat': datetime.now(),
        'sub': str(user_id),
        'type': 'access'
    }
    return jwt.encode(payload, settings.secret_key, algorithm='HS256')


def validate_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=['HS256'])
        if payload.get('type') != 'access':
            raise Exception('Неверный тип токена')
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return Exception('Токен истёк')
    except jwt.InvalidTokenError:
        return Exception('Неверный токен')


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
