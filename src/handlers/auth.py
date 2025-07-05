from flask import request, make_response, g
from flask_restx import Resource

from src.db import db
from src.db import models
from src.auth import tokens
from src.schemas import user_schemas
from src.swagger_schemas.swagger_models import auth_ns
from src.auth.decorators import auth_required


@auth_ns.route("/refresh", methods=["POST"])
class RefreshToken(Resource):
    @auth_required
    def post(self):
        if not g.user:
            return {'message': 'No user found'}, 401
        access_token = tokens.generate_access_token(g.user.id)
        return {'access_token': access_token}, 201


@auth_ns.route("/me", methods=["POST"])
class Me(Resource):
    @auth_required
    def get(self):
        if not g.user:
            return {'message': 'No user found'}, 404
        return user_schemas.UserSchema().dump(g.user)

@auth_ns.route("/logout", methods=["POST"])
class LogoutToken(Resource):
    @auth_required
    def post(self):
        resp = make_response({'message': 'Вы вышли из системы'})
        resp.set_cookie("auth_reader", max_age=0, httponly=True, samesite='Lax')
        resp.set_cookie("refresh_token", max_age=0, httponly=True, samesite='Lax')
        token = models.RefreshToken.get_by_token(token=request.cookies.get("refresh_token"))
        if not token:
            return {'message': 'No refresh token'}, 201
        db.session.delete(token)
        db.session.commit()
        return resp
