import jwt
import datetime

# WARNING: This default key is insecure. Callers should provide a secure secret.
DEFAULT_SECRET_KEY = 'your_secret_key_here'

def generate_jwt(payload, secret_key=None, expiration_minutes=30):
    secret = secret_key or DEFAULT_SECRET_KEY
    if not secret:
        raise ValueError("Secret key is required for JWT generation")
        
    expiration = datetime.datetime.now() + datetime.timedelta(minutes=expiration_minutes)
    # Ensure payload doesn't already have exp or handle it? 
    # Current logic overrides it.
    payload_to_encode = payload.copy() # Avoid mutating original payload
    payload_to_encode.update({"exp": expiration})
    
    token = jwt.encode(payload_to_encode, secret, algorithm="HS256")
    return token

def verify_jwt(token, secret_key=None):
    secret = secret_key or DEFAULT_SECRET_KEY
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
