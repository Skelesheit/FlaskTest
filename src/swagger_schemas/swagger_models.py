from flask_restx import fields, Namespace

user_ns = Namespace("users", description="Операции с пользователями")
auth_ns = Namespace("auth", description="Аутентификация")
mail_ns = Namespace("mail", description="Работа с mail")
dadata_ns = Namespace("dadata", description="Dadata сервис")
# Login
login_model = user_ns.model("Login", {
    "email": fields.String(required=True, description="Email"),
    "password": fields.String(required=True, description="Пароль"),
})

# Register
register_model = user_ns.model("Register", {
    "email": fields.String(required=True, description="Email", example="user@example.com"),
    "password": fields.String(required=True, description="Пароль", min_length=6),
    "captchaToken": fields.String(required=True, description="токен от яндекса"),
})

# Contact
contact_model = user_ns.model("Contact", {
    "city": fields.String(required=True, description="Город"),
    "phone": fields.String(required=True, description="Телефон", example="89999999999"),
    "address": fields.String(required=True, description="Адрес"),
})

# IndividualProfile
individual_profile_model = user_ns.model("IndividualProfile", {
    "first_name": fields.String(required=True),
    "last_name": fields.String(required=True),
    "patronymic": fields.String(required=True),
})

# LegalEntityProfile
legal_entity_profile_model = user_ns.model("LegalEntityProfile", {
    "org_name": fields.String(required=True),
    "kpp": fields.String(required=True),
    "opf_full": fields.String(required=True),
    "opf_short": fields.String(required=True),
})

#  LegalEntity
legal_entity_model = user_ns.model("LegalEntity", {
    "user_id": fields.Integer(required=True),
    "ogrn": fields.String(required=True),
    "inn": fields.String(required=True),
    "management_name": fields.String(required=True),
    "legal_entity_profile": fields.Nested(legal_entity_profile_model)
})

# User (с вложенностями)
user_model_form = user_ns.model("User", {
    "user_type": fields.String(enum=["ИП", "Юр. лицо", "Физ. лицо"]),
    "is_verified": fields.Boolean(),
    "contact": fields.Nested(contact_model),
    "individual_profile": fields.Nested(individual_profile_model),
    "legal_entity": fields.Nested(legal_entity_model),
})
