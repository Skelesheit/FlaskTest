from config import settings
from src.db import db
from src.db.models import User
from src.utils import hash_password

admin = User(email=settings.admin_email,
             password=(hash_password(settings.admin_password)),
             is_verified=True,
             is_admin=True)
db.session.add(admin)
db.session.commit()
