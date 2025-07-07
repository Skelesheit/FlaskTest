from functools import wraps

from flask import request, jsonify, g

from src.auth import tokens
from src.db.models import User


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'message': 'Not authorized'}, 401
        token = auth_header.split(' ')[1]
        try:
            user_id = tokens.validate_token(token)
        except Exception as e:
            return {'message': str(e)}, 401
        g.user = User.get_by_id(user_id)
        return f(*args, **kwargs)
    return decorated_function



def user_verified(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user.is_verified:
            return f(*args, **kwargs)
        return jsonify({'message': 'Not verified'}), 401
