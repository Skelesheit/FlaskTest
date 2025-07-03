import bcrypt


def hash_password(password: str) -> str:
    byte_password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(byte_password, salt).decode('utf-8')


def validate(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed
