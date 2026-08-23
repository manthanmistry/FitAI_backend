from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.auth_models import AuthUser
from app.auth_service import (
    normalize_email,
    hash_password,
    verify_password,
    create_access_token,
    user_response,
)
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
def signup(payload: SignupIn, db: Session = Depends(get_db)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    email = normalize_email(payload.email)

    if db.query(AuthUser).filter(AuthUser.email == email).first():
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    user = AuthUser(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": user_response(user),
    }


@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = (
        db.query(AuthUser)
        .filter(AuthUser.email == normalize_email(payload.email))
        .first()
    )

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": user_response(user),
    }
