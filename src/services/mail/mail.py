from flask_mail import Message
from flask import current_app
from src.auth.tokens import generate_access_token
from config import settings
from src.services.mail.conts import generate_html, subject
from src.services.mail.extentions import mail

def send_registration_email(user_id: int, email: str) -> None:
    token = generate_access_token(user_id)
    confirm_url=f"{settings.base_url}/mail/confirm/{token}"
    print(f"Отправка письма на {email}")
    msg = Message(
        subject=subject,
        recipients=[email],
        html=generate_html(confirm_url),
        sender=settings.mail_default_sender,
    )
    with current_app.app_context():
        mail.send(msg)