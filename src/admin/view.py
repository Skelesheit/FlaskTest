from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request, g
from flask_login import current_user

class AdminModelView(ModelView):
    def is_accessible(self):
        return g.get("user") and g.user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin/login"))  # или "/auth/login"
