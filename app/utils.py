import datetime
from typing import Optional

from fastapi import HTTPException
from passlib.context import CryptContext
from jose import JWTError, jwt
import random
import string

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def generate_verification_code(length: int = 6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def create_access_token(data: dict, secret_key: str, algorithm: str,
                        expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_access_token(token: str, secret_key: str, algorithm: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class CSPMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, csp_policy: str):
        super().__init__(app)
        self.csp_policy = csp_policy

    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers['Content-Security-Policy'] = self.csp_policy
        return response


csp_policy = (
    "default-src 'self'; "
    "script-src 'self' https://trusted.cdn.com; "
    "style-src 'self' https://trusted.cdn.com; "
    "img-src 'self' data:; "
    "connect-src 'self';"
)

#alembic upgrade head
#alembic revision --autogenerate -m "Add created_date to User"
#uvicorn app.main : app --reload