from flask import request, make_response, g
from flask_restx import Resource
from marshmallow import ValidationError

from src import utils
from src.auth import tokens
from src.auth.decorators import auth_required, user_verified
from src.db import db
from src.db.enums import UserType
from src.db.models import User
from src.schemas import user_schemas
from src.services.captcha.yandex import verify_yandex_captcha
from src.swagger_schemas import swagger_models
from src.swagger_schemas.swagger_models import user_ns


@user_ns.route("/register", methods=["POST"])
class UserRegister(Resource):
    @user_ns.expect(swagger_models.register_model)
    @user_ns.response(201, 'Пользователь успешно создан')
    @user_ns.response(400, 'Ошибочные данные')
    def post(self):
        data = request.get_json()
        try:
            validated_data = user_schemas.RegisterSchema().load(data)
        except ValidationError as e:
            return {'message': 'Validation failed', 'errors': e.messages}, 400

        captcha_token = validated_data.get("captchaToken")
        if not captcha_token or not verify_yandex_captcha(captcha_token):
            return {"message": "Капча не пройдена"}, 400

        if User.has_email(validated_data['email']):
            return {'message': 'Такой пользователь уже существует'}, 400
        # теперь создание пользователя
        hashed = utils.hash_password(validated_data['password'])
        user = User(
            email=validated_data['email'],
            password=hashed,
        )
        db.session.add(user)
        db.session.commit()
        return {'message': 'Пользователь успешно зарегистрирован'}, 201


@user_ns.route("/login", methods=["POST"])
class UserLogin(Resource):
    @user_ns.expect(swagger_models.login_model)
    @user_ns.response(201, 'Пользователь успешно вошёл')
    @user_ns.response(400, 'Ошибочные данные')
    def post(self):
        data = request.get_json()
        try:
            validated_data = user_schemas.LoginSchema().load(data)
        except ValidationError as e:
            return {'message': 'Validation failed', 'errors': e.messages}, 400
        user = User.get_by_email(validated_data['email'])
        if not user or user.check_password(validated_data['password']):
            return ('message', 'Пользователь ввёл неправильные данные'), 401
        refresh_token = tokens.create_refresh_token(user.id)
        access_token = tokens.generate_access_token(user.id)
        response = make_response({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 900  # 15 минут
        }, 201)
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=False,  # True если HTTPS
            samesite='Lax',
            max_age=60 * 60 * 24 * 7  # 7 дней
        )
        return response


@user_ns.route("/fill-data", methods=["POST"])
class UserFillData(Resource):
    @auth_required
    @user_verified
    @user_ns.expect(swagger_models.user_model_form)
    def post(self):
        data = request.get_json()
        try:
            validated_data = user_schemas.UserTypeSchema().load(data)
            user_type = UserType(validated_data['user_type'])
        except ValidationError as e:
            return {'message': 'Validation failed', 'errors': e.messages}, 400
        try:
            match validated_data['type']:
                case user_type.Individual:
                    validated_data = user_schemas.IndividualProfileSchema().load(data['form'])
                case user_type.LegalEntity:
                    validated_data = user_schemas.LegalEntityProfileSchema().load(data['form'])
                case user_type.LegalEntityProfile:
                    validated_data = user_schemas.LegalEntityProfileSchema().load(data['form'])
        except ValidationError as e:
            return {'message': 'Validation failed', 'errors': e.messages}, 400
        validated_data['user_id'] = g.user.id
        db.session.add(validated_data)
        db.session.commit()

        return {'message', 'Forms filled successfully'}, 201
