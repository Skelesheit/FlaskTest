from flask import request, make_response, g
from flask_restx import Resource
from marshmallow import ValidationError
from pprint import pprint

from src.auth import tokens
from src.auth.decorators import auth_required, user_verified
from src.db import db
from src.db.models import User, RefreshToken
from src.schemas import user_schemas
from src.services.captcha.yandex import verify_yandex_captcha
from src.services.mail.mail import send_registration_email
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
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        if not captcha_token:
            return {"message": "Капча не пройдена"}, 400
        if not verify_yandex_captcha(captcha_token, ip):
            return {"message": "Капча не пройдена"}, 400
        email, password = validated_data['email'], validated_data['password']
        if User.has_email(email):
            return {'message': 'Такой пользователь уже существует'}, 400
        # теперь создание пользователя
        user = User.create(email, password)
        # отправляем письмо для верификации
        send_registration_email(user.id, email)
        return {'message': 'Пользователь успешно зарегистрирован, проверяйте почту'}, 201


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
        refresh_token = RefreshToken.create(user.id)
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
    @user_ns.doc(security='BearerAuth')
    @auth_required
    @user_ns.expect(swagger_models.fill_data_model)
    @user_ns.doc(
        description="Endpoint for filling user data depending on type",
        body={
            "type": "object",  # 👈 это заставляет Swagger показать JSON-поле
            "required": ["user_type", "fill", "contact"],
            "properties": {
                "user_type": {
                    "type": "string",
                    "enum": ["ИП", "Юр. лицо", "Физ. лицо"]
                },
                "fill": {
                    "type": "object",
                    "description": "Данные анкеты, зависят от user_type"
                },
                "contact": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "phone": {"type": "string"},
                        "address": {"type": "string"}
                    }
                }
            },
            "example": {
                "user_type": "Физ. лицо",
                "fill": {
                    "first_name": "Иван",
                    "last_name": "Иванов",
                    "patronymic": "Иванович"
                },
                "contact": {
                    "city": "Москва",
                    "phone": "89999999999",
                    "address": "Ул. Пушкина"
                }
            }
        }
    )
    def post(self):
        data = request.get_json()
        pprint(data, indent=2)
        try:
            schema = user_schemas.FillShema()
            schema.context = {"user": g.user}
            validated_data = schema.load(data)
            profile = validated_data["profile"]
            contact = validated_data["contact"]
        except ValidationError as e:
            print(e.messages)
            return {'message': 'Validation failed', 'errors': e.messages}, 400
        db.session.add(profile)
        db.session.add(contact)
        db.session.commit()
        return {'message': 'Forms filled successfully'}, 201
