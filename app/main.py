from typing import Dict

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import schemas, models, crud, utils
from .database import SessionLocal, engine, get_db
import os
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta

from .utils import decode_access_token, CSPMiddleware, csp_policy

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 100

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
# Allow CORS for specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trust specific hosts (e.g., domain names)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"]
)
app.add_middleware(CSPMiddleware, csp_policy=csp_policy)

models.Base.metadata.create_all(bind=engine)


@app.post("/signup/", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    check_mobile = crud.get_user_by_mobile(db, phone_number=user.phone_number)
    if check_mobile:
        raise HTTPException(status_code=400, detail="Mobile already registered")

    return crud.create_user(db=db, user=user)


@app.post("/login/")
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not utils.verify_password(user.password, db_user.hashed_password):
        db_user.unsuccessful_attempts += 1
        if db_user.unsuccessful_attempts >= 3:
            raise HTTPException(status_code=400, detail="Account locked due to multiple failed attempts")
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid email or password")
    db_user.unsuccessful_attempts = 0  # Reset unsuccessful attempts after successful login
    db.commit()
    access_token = utils.create_access_token(data={"sub": db_user.email}, secret_key=SECRET_KEY, algorithm=ALGORITHM,
                                             expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/forgot-password/")
def forgot_password(request: schemas.ForgotPassword, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=request.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    verification_code = utils.generate_verification_code()
    crud.update_verification_code(db, user=db_user, code=verification_code)
    # Send the verification code by email (implementation not included)
    return {"msg": "Verification code sent to your email"}


@app.post("/change-password/")
def change_password(request: schemas.ChangePassword, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.verification_code == request.verification_code).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    crud.update_user_password(db, user=db_user, new_password=request.new_password)
    return {"msg": "Password updated successfully"}


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token, SECRET_KEY, ALGORITHM)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.get_user_by_email(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


@app.post("/user_details")
async def user_details(request: schemas.Userdetail, db: Session = Depends(get_db),
                       current_user: Dict[str, str] = Depends(get_current_user)):
    db_user = db.query(models.User).filter(models.User.id == request.id).first()
    print(current_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

