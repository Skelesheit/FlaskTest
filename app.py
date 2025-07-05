from flask import Flask
from flask_restx import Api

from config import settings
from src.handlers.auth import auth_ns
from src.handlers.user import user_ns
from src.handlers.mail import mail_ns
from src.services.mail.extentions import init_extensions


def create_app():
    app = Flask(__name__)

    app.config.update(
        MAIL_SERVER=settings.mail_server,
        MAIL_PORT=settings.mail_port,
        MAIL_USE_TLS=settings.mail_use_tls,
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_DEFAULT_SENDER=settings.mail_default_sender
    )

    init_extensions(app)

    api = Api(app, title="NeuroCam", version="1.0", description="Документация через Swagger")
    api.add_namespace(user_ns, path="/user")
    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(mail_ns, path="/mail")

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host=settings.backend_host,
            port=settings.backend_port,
            debug=settings.backend_debug)
