import jwt
from datetime import datetime, timedelta

# Настройки
secret = "C)hgODfy[!folMKWVp2zzL%J>d!?__r]l>&/>W$*&y?i@N3YE@?bME[YqO*_C!!/c^ri1_MMvm+$SKgUa/ty<9lM-C/6^>F5]i}#"

# Генерация токена
now = datetime.utcnow()
payload = {
    'exp': now + timedelta(minutes=15),
    'iat': now,
    'sub': '1',
    'type': 'access'
}

token = jwt.encode(payload, secret, algorithm="HS256")
print("🔐 Сгенерированный токен:\n", token)

# Валидация токена
decoded = jwt.decode(
    token,
    secret,
    algorithms=["HS256"],
    options={"require": ["exp", "iat", "sub", "type"]},
    leeway=10  # На всякий случай
)

print("✅ Расшифрованный payload:")
for key, value in decoded.items():
    print(f"  {key}: {value}")
