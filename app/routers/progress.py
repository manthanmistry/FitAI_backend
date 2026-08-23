from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import WeightLogIn, WorkoutLogIn, WaterLogIn
from app.calculations import calculate_bmi
from app.deps import get_profile_user

router = APIRouter(tags=["progress"])


@router.post("/progress/weight")
def log_weight(payload: WeightLogIn, db: Session = Depends(get_db), user: models.User = Depends(get_profile_user)):
    bmi = calculate_bmi(payload.weight_kg, user.height_cm)
    log = models.WeightLog(user_id=user.id, weight_kg=payload.weight_kg, bmi=bmi)
    db.add(log)
    db.commit()
    return {"status": "logged", "bmi": bmi}


@router.post("/progress/workout")
def log_workout(payload: WorkoutLogIn, db: Session = Depends(get_db), user: models.User = Depends(get_profile_user)):
    log = models.WorkoutLog(
        user_id=user.id,
        activity=payload.activity,
        duration_min=payload.duration_min,
        calories_burned=payload.calories_burned or 0,
    )
    db.add(log)
    db.commit()
    return {"status": "logged"}


@router.post("/progress/water")
def log_water(payload: WaterLogIn, db: Session = Depends(get_db), user: models.User = Depends(get_profile_user)):
    log = models.WaterLog(user_id=user.id, amount_l=payload.amount_l)
    db.add(log)
    db.commit()
    return {"status": "logged"}


@router.get("/progress")
def get_progress(db: Session = Depends(get_db), user: models.User = Depends(get_profile_user)):
    weight_logs = (
        db.query(models.WeightLog)
        .filter(models.WeightLog.user_id == user.id)
        .order_by(models.WeightLog.logged_at.asc())
        .all()
    )
    workout_logs = (
        db.query(models.WorkoutLog)
        .filter(models.WorkoutLog.user_id == user.id)
        .order_by(models.WorkoutLog.logged_at.asc())
        .all()
    )
    water_logs = (
        db.query(models.WaterLog)
        .filter(models.WaterLog.user_id == user.id)
        .order_by(models.WaterLog.logged_at.asc())
        .all()
    )

    streak = 0
    if workout_logs:
        days_with_workout = sorted({w.logged_at.date() for w in workout_logs}, reverse=True)
        cursor = datetime.utcnow().date()
        for day in days_with_workout:
            if day == cursor:
                streak += 1
                cursor -= timedelta(days=1)
            else:
                break

    return {
        "weight_logs": [
            {"date": w.logged_at.isoformat(), "weight_kg": w.weight_kg, "bmi": w.bmi}
            for w in weight_logs
        ],
        "workout_logs": [
            {
                "date": w.logged_at.isoformat(),
                "activity": w.activity,
                "duration_min": w.duration_min,
                "calories_burned": w.calories_burned,
            }
            for w in workout_logs
        ],
        "water_logs": [
            {"date": w.logged_at.isoformat(), "amount_l": w.amount_l} for w in water_logs
        ],
        "workout_streak_days": streak,
    }
