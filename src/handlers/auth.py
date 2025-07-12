import json
from pprint import pprint

from flask import request, make_response, g, jsonify, Response, current_app
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
        if token is None:
            return {"message": "Invalid refresh token"}, 401
        user = token.user
        # берём юзера у которого есть refresh:
        # затем либо logout, либо создать новый refresh
        if token.expired:
            print(f'refresh токен реально истёк лололо: {token.id, token.expired}')
            token.delete_token()
            return {"message": "Refresh token has expired."}, 401
        # сделаем по соображениям безопасности - обновляем и refresh тоже
        # а стоит ли так делать? Пока оставлю вот так..
        refresh_token = models.RefreshToken.create(user.id)
        access_token = tokens.generate_access_token(user.id)
        resp = current_app.response_class(
            response=json.dumps({"access_token": access_token}),
            status=200,
            mimetype='application/json'
        )
        resp.set_cookie("refresh_token", refresh_token, secure=False, httponly=True, samesite='Lax')
        return resp


@auth_ns.route("/me", methods=["GET"])
class Me(Resource):
    @auth_ns.doc(security='BearerAuth')
    @auth_required
    def get(self):
        if not g.user:
            return {'message': 'No user found'}, 404
        print("We stay there!")
        pprint(g.user, indent=2)
        pprint(user_schemas.UserSchema().dump(g.user), indent=2)
        return user_schemas.UserSchema().dump(g.user)

@auth_ns.route("/logout", methods=["POST"])
class LogoutToken(Resource):
    @auth_ns.doc(security='BearerAuth')
    @auth_required
    def post(self):
        models.RefreshToken.delete_by_token(request.cookies.get("refresh_token"))
        resp = current_app.response_class(
            response=json.dumps({"message": "Successfully logged out."}),
            status=200,
            mimetype='application/json'
        )
        resp.set_cookie("refresh_token", '', max_age=0, httponly=True, samesite='Lax')
        resp.set_cookie("auth_reader", '', max_age=0, httponly=True, samesite='Lax')

        return resp
