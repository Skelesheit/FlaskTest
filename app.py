from flask import Flask
from flask_restx import Api

from config import settings
from src.handlers.user import user_ns
from src.handlers.auth import auth_ns

app = Flask(__name__)

api = Api(app, title="NeuroCam", version="1.0", description="Документация через Swagger")
api.add_namespace(user_ns, path="/user")
api.add_namespace(auth_ns, path="/auth")

if __name__ == '__main__':
    app.run(host=settings.backend_host,
            port=settings.backend_port,
            debug=settings.backend_debug)

