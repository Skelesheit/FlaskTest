from flask import redirect
from flask_restx import Resource

from config import settings
from src.db import db
from src.auth.tokens import decode_email_token
from src.db.models import User
from src.swagger_schemas.swagger_models import mail_ns

@mail_ns.route("/confirm/<string:token>")
class ConfirmMail(Resource):
    def get(self, token):
        user_id = decode_email_token(token)
        if not user_id:
            return {"message": "Invalid email token"}
        is_verified = User.verify_email(user_id)
        if not is_verified:
            return {"message": "User not verified"}
        return redirect(f"{settings.frontend_url}/email-confirmed", code=302)
