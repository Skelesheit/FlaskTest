from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from src.admin.view import AdminView
from src.db import db
from src.db.models import User, RefreshToken, Contact, IndividualProfile, LegalEntity, LegalEntityProfile


def init_admin(app):
    admin = Admin(app, name="Админка", template_mode="bootstrap4")

    admin.add_view(AdminView(User, db.session, name='Users', endpoint='admin_user'))
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(RefreshToken, db.session))
    admin.add_view(ModelView(Contact, db.session))
    admin.add_view(ModelView(IndividualProfile, db.session))
    admin.add_view(ModelView(LegalEntity, db.session))
    admin.add_view(ModelView(LegalEntityProfile, db.session))
