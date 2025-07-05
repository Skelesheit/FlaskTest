from functools import wraps
from flask import request, jsonify, g
from src.db import db
from src.db import models
import tokens
from src.db.models import User


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer'):
            token = auth_header.split(' ')[1]
        else:
            token = request.cookies.get('access_token')
        if not token:
            return jsonify({'message': 'Not authorized'}), 401
        try:
            user_id = tokens.validate_token(token)
        except Exception as e:
            return jsonify({'message': str(e)}), 401
        g.user = User.get_by_id(user_id)
        return f(*args, **kwargs)
    return decorated_function

def user_verified(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user.is_verified:
            return f(*args, **kwargs)
        return jsonify({'message': 'Not verified'}), 401


