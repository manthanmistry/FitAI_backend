from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.auth_models import AuthUser
from app.deps import get_current_user

router = APIRouter(tags=["history"])


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    auth_user: AuthUser = Depends(get_current_user),
):
    user = db.query(models.User).filter(models.User.auth_user_id == auth_user.id).first()
    if not user:
        return {
            "user": {
                "id": None,
                "name": auth_user.name,
                "email": auth_user.email,
                "goal": None,
                "diet_type": None,
            },
            "plans": [],
        }

    plans = (
        db.query(models.Plan)
        .filter(models.Plan.user_id == user.id)
        .order_by(models.Plan.created_at.desc())
        .all()
    )
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": auth_user.email,
            "goal": user.goal,
            "diet_type": user.diet_type,
        },
        "plans": [
            {
                "id": p.id,
                "bmi": p.bmi,
                "bmi_category": p.bmi_category,
                "daily_calories": p.daily_calories,
                "content_markdown": p.content_markdown,
                "created_at": p.created_at,
            }
            for p in plans
        ],
    }
