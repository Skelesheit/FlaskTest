from marshmallow import Schema, fields, validate, ValidationError, post_load
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from src.db import models, db
from src.db.enums import UserType


class UserSchema(SQLAlchemySchema):
    class Meta:
        model = models.User
        load_instance = True
        include_relationships = True

    id = auto_field()
    email = auto_field()
    created_at = auto_field()
    user_type = auto_field()
    is_verified = auto_field()
    is_filled = auto_field()
    contact = Nested('ContactSchema', allow_none=True)


class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.String(required=True, validate=validate.Length(min=6))
    captchaToken = fields.String(required=True)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class FillShema(Schema):
    user_type = fields.String(required=True)
    fill = fields.Raw(required=True)  # 👈 его сам обрабатываешь
    contact = fields.Raw(required=False, allow_none=True)  # 👈 тоже руками

    @post_load
    def process_fill(self, data, **kwargs):
        user = self.context["user"]
        user_type = UserType(data['user_type'])
        fill_data = data['fill']
        contact_data = data.get('contact')
        fill_data['user_id'] = user.id

        # --- основной профиль ---
        match user_type:
            case user_type.Individual:
                profile_schema = IndividualProfileSchema()
            case user_type.LegalEntity:
                profile_schema = LegalEntitySchema()
            case user_type.LegalEntityProfile:
                profile_schema = LegalEntitySchema()
            case _:
                raise ValidationError('Невалидный user_type')
        profile = profile_schema.load(fill_data, session=db.session)
        # --- контакт ---
        contact_schema = ContactSchema(session=db.session)
        contact = contact_schema.load(contact_data)
        contact.user_id = user.id
        return {"profile": profile, "contact": contact}




class ContactSchema(SQLAlchemySchema):
    class Meta:
        model = models.Contact
        load_instance = True
        sqla_session = db.session

    id = auto_field()
    city = auto_field()
    phone = auto_field()
    address = auto_field()


class IndividualProfileSchema(SQLAlchemySchema):
    class Meta:
        model = models.IndividualProfile
        load_instance = True
        sqla_session = db.session

    id = auto_field()
    user_id = auto_field()
    first_name = auto_field()
    last_name = auto_field()
    patronymic = auto_field()


class LegalEntitySchema(SQLAlchemySchema):
    class Meta:
        model = models.LegalEntity
        load_instance = True
        include_relationship = True
        sqla_session = db.session

    id = auto_field()
    user_id = auto_field()
    ogrn = auto_field()
    inn = auto_field()
    management_name = auto_field()
    legal_entity_profile = fields.Nested('LegalEntityProfileSchema', required=False, allow_none=True)


class LegalEntityProfileSchema(SQLAlchemySchema):
    class Meta:
        model = models.LegalEntityProfile
        load_instance = True
        include_relationship = True
        sqla_session = db.session

    id = auto_field()
    legal_id = auto_field(dump_only=True)
    org_name = auto_field()
    kpp = auto_field()
    opf_full = auto_field()
    opf_short = auto_field()
