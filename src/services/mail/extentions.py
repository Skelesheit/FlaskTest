from flask_mail import Mail

mail = Mail()

def init_extensions(app):
    mail.init_app(app)