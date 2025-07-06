import secrets
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import Column, Integer, String, func
from sqlalchemy import DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from config import settings
from src.auth import tokens
from src.db import db
from src.utils import validate, hash_password

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(), nullable=False)
    created_at = Column(DateTime, default=func.now())
    user_type = Column(ENUM('ИП', 'Юр. лицо', 'Физ. лицо', name='user_type_enum' ), )
    is_verified = Column(Boolean, nullable=False, default=False)
    is_filled = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    token = relationship('RefreshToken', back_populates='user', uselist=False, cascade='all, delete-orphan')
    contact = relationship('Contact', back_populates='user', uselist=False, cascade='all, delete-orphan')
    individual_profile = relationship('IndividualProfile', back_populates='user', uselist=False,
                                      cascade='all, delete-orphan')
    legal_entity = relationship('LegalEntity', back_populates='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"

    @classmethod
    def create(cls, email, password) -> 'User':
        password_hash = hash_password(password)
        user = User(email=email, password=password_hash)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def verify_email(cls, user_id: int) -> bool:
        updated = db.session.query(cls).filter_by(id=user_id).update({'is_verified': True})
        db.session.commit()
        return updated > 0

    @classmethod
    def get_by_id(cls, user_id: int) -> 'User | None':
        return db.session.query(cls).filter_by(id=user_id).first()

    def check_password(self, password: str) -> bool:
        return validate(password, self.password)

    @classmethod
    def has_email(cls, email: str) -> bool:
        return db.session.query(cls).filter_by(email=email).first() is not None

    @classmethod
    def get_by_email(cls, email: str) -> 'User | None':
        return db.session.query(cls).filter_by(email=email).first()


class RefreshToken(Base):
    __tablename__ = 'token'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    token = Column(String(), nullable=False)
    expires_at = Column(DateTime(), nullable=False)

    user = relationship('User', back_populates='token', uselist=False)

    @classmethod
    def get_by_token(cls, token: str) -> 'RefreshToken':
        return db.session.query(cls).filter_by(token=token).first()

    @classmethod
    def delete_by_token(cls, token: str) -> None:
        db.session.query(cls).filter_by(token=token).delete()
        db.session.commit()

    @property
    def expired(self) -> bool:
        return self.expires_at > datetime.now()

    @classmethod
    def create(cls, user_id: int) -> str:
        cls.delete_by_id(user_id)
        token = secrets.token_urlsafe(64)
        expires = datetime.now() + timedelta(days=settings.expire_refresh_token_days)
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires
        )
        db.session.add(refresh_token)
        db.session.commit()
        return token

    @classmethod
    def delete_by_id(cls, user_id: int) -> 'None':
        db.session.where(cls.user_id == user_id).delete()
        db.session.commit()

    @classmethod
    def delete_token(cls) -> None:
        db.session.delete(cls.token)
        db.session.commit()


# контактная информация
class Contact(Base):
    __tablename__ = 'contact_info'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    phone = Column(String(15), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(300), nullable=False)

    user = relationship('User', back_populates='contact', uselist=False)


# физическое лицо
class IndividualProfile(Base):
    __tablename__ = 'profile_individual'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    patronymic = Column(String(100), nullable=False)

    user = relationship('User', back_populates='individual_profile', uselist=False)


# юридическое лицо (база)
class LegalEntity(Base):
    __tablename__ = 'legal_entity'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    ogrn = Column(String(13), nullable=False)
    inn = Column(String(12), nullable=False)
    management_name = Column(String(300))

    user = relationship('User', back_populates='legal_entity', uselist=False)
    legal_entity_profile = relationship('LegalEntityProfile', back_populates='legal_entity', uselist=False,
                                        cascade='all, delete-orphan')


# юридическое лицо - расширение (не ИП)
class LegalEntityProfile(Base):
    __tablename__ = 'profile_legal_entity'
    id = Column(Integer, primary_key=True)
    legal_id = Column(Integer, ForeignKey('legal_entity.id'), nullable=False)
    org_name = Column(String(), nullable=False)
    kpp = Column(String(9), nullable=False)
    opf_full = Column(String(), nullable=False)
    opf_short = Column(String(30), nullable=False)

    legal_entity = relationship('LegalEntity', back_populates='legal_entity_profile', uselist=False)
