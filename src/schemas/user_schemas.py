from marshmallow import Schema, fields, validate
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from src.db import models


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
    contact = Nested('ContactSchema')
    individual_profile = auto_field()
    legal_entity = auto_field()


class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.String(required=True, validate=validate.Length(min=6))
    user_type = fields.String(required=True, validate=validate.OneOf(['ИП', 'Юр. лицо', 'Физ. лицо']))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class ContactSchema(SQLAlchemySchema):
    class Meta:
        model = models.Contact
        load_instance = True

    id = auto_field()
    city = auto_field()
    phone = auto_field()
    address = auto_field()


class IndividualProfileSchema(SQLAlchemySchema):
    class Meta:
        model = models.IndividualProfile
        load_instance = True

    id = auto_field()
    first_name = auto_field()
    last_name = auto_field()
    patronymic = auto_field()


class LegalEntitySchema(SQLAlchemySchema):
    class Meta:
        model = models.LegalEntity
        load_instance = True
        include_relationship = True

    id = auto_field()
    user_id = auto_field()
    ogrn = auto_field()
    inn = auto_field()
    management_name = auto_field()
    legal_entity_profile = fields.Nested('LegalEntityProfileSchema', exclude=('legal_entity',))


class LegalEntityProfileSchema(SQLAlchemySchema):
    class Meta:
        model = models.LegalEntityProfile
        load_instance = True
        include_relationship = True

    id = auto_field()
    legal_id = auto_field()
    org_name = auto_field()
    kpp = auto_field()
    opf_full = auto_field()
    opf_short = auto_field()
    legal_entity = fields.Nested(LegalEntitySchema, only=("id",))


class UserTypeSchema(SQLAlchemySchema):
    class Meta:
        model = models.User
        load_instance = True
        include_relationships = True
        fields = ('user_type',)
