from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth_models import AuthUser
from app.auth_service import get_user_from_token
from app.database import get_db
from app import models

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> AuthUser:
    if not creds or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please sign in to continue.",
        )
    return get_user_from_token(db, creds.credentials)


def get_profile_user(
    auth_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> models.User:
    user = db.query(models.User).filter(models.User.auth_user_id == auth_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No fitness profile yet. Generate a plan first.",
        )
    return user


def apply_profile(user: models.User, profile) -> models.User:
    user.name = profile.name
    user.age = profile.age
    user.gender = profile.gender.value
    user.height_cm = profile.height_cm
    user.weight_kg = profile.weight_kg
    user.target_weight_kg = profile.target_weight_kg
    user.activity_level = profile.activity_level.value
    user.sleep_hours = profile.sleep_hours
    user.stress_level = profile.stress_level.value
    user.water_intake_l = profile.water_intake_l
    user.goal = profile.goal.value
    user.workout_experience = profile.workout_experience.value
    user.workout_days_per_week = profile.workout_days_per_week
    user.workout_duration_min = profile.workout_duration_min
    user.workout_location = profile.workout_location.value
    user.diet_type = profile.diet_type.value
    user.allergies = profile.allergies or ""
    user.medical_conditions = profile.medical_conditions or ""
    return user
