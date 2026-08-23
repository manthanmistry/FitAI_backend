from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

router = APIRouter(tags=["history"])


@router.get("/history")
def get_history(user_id: int = Query(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plans = (
        db.query(models.Plan)
        .filter(models.Plan.user_id == user_id)
        .order_by(models.Plan.created_at.desc())
        .all()
    )
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "goal": user.goal,
            "diet_type": user.diet_type,
        },
        "plans": [
            {
                "id": p.id,
                "bmi": p.bmi,
                "bmi_category": p.bmi_category,
                "daily_calories": p.daily_calories,
                "created_at": p.created_at,
            }
            for p in plans
        ],
    }
