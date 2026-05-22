import jwt
from decouple import config
from datetime import datetime, timedelta

def encode_token(data):
    key = config('SECRET_KEY')
    expiration_time = datetime.utcnow() + timedelta(days=1)  # You can adjust the expiration time
    payload = {'exp': expiration_time, **data}
    return jwt.encode(payload, key, algorithm='HS256').decode('utf-8')

def decode_token(token):
    key = config('SECRET_KEY')
    try:
        return jwt.decode(token, key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        # Handle expired token
        return None
    except jwt.InvalidTokenError:
        # Handle invalid token
        return None
