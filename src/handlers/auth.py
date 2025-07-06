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
    def post(self):
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return {"message": "No refresh token provided."}, 401
        token = models.RefreshToken.get_by_token(refresh_token)
        user = token.user
        # берём юзера у которого есть refresh:
        # затем либо logout, либо создать новый refresh
        if token.expired:
            token.delete_token()
            return {"message": "Refresh token has expired."}, 401
        # сделаем по соображениям безопасности - обновляем и refresh тоже
        # а стоит ли так делать? Пока оставлю вот так..
        refresh_token = models.RefreshToken.create(user.id)
        access_token = tokens.generate_access_token(user.id)
        resp = make_response({
            "access_token": access_token
        })
        resp.set_cookie("refresh_token", refresh_token, httponly=True, samesite='Lax')
        return resp, 200



@auth_ns.route("/me", methods=["GET"])
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
        models.RefreshToken.delete_by_token(request.cookies.get("refresh_token"))
        return resp
