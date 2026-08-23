import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserProfileIn
from app.calculations import full_calculation
from app import models
from app.ai_service import stream_plan
from app.auth_models import AuthUser
from app.deps import get_current_user, apply_profile

router = APIRouter(tags=["plan"])


@router.post("/generate-plan")
def generate_plan(
    profile: UserProfileIn,
    db: Session = Depends(get_db),
    auth_user: AuthUser = Depends(get_current_user),
):
    calc = full_calculation(
        weight_kg=profile.weight_kg,
        height_cm=profile.height_cm,
        age=profile.age,
        gender=profile.gender.value,
        activity_level=profile.activity_level.value,
        goal=profile.goal.value,
    )

    user = db.query(models.User).filter(models.User.auth_user_id == auth_user.id).first()
    if user:
        apply_profile(user, profile)
    else:
        user = models.User(auth_user_id=auth_user.id)
        apply_profile(user, profile)
        db.add(user)
    db.commit()
    db.refresh(user)

    plan_row = models.Plan(
        user_id=user.id,
        bmi=calc["bmi"], bmi_category=calc["bmi_category"],
        bmr=calc["bmr"], tdee=calc["tdee"],
        daily_calories=calc["daily_calories"],
        protein_g=calc["protein_g"], carbs_g=calc["carbs_g"], fat_g=calc["fat_g"],
        water_l=calc["water_l"], content_markdown="",
    )
    db.add(plan_row)
    db.commit()
    db.refresh(plan_row)

    profile_dict = profile.model_dump()
    plan_id = plan_row.id
    user_id = user.id

    def event_generator():
        collected = []
        meta = {"type": "meta", "user_id": user_id, "plan_id": plan_id, "calculations": calc}
        yield f"data: {json.dumps(meta)}\n\n"

        try:
            for chunk in stream_plan(profile_dict, calc):
                collected.append(chunk)
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
        finally:
            full_text = "".join(collected)
            from app.database import SessionLocal
            session = SessionLocal()
            try:
                row = session.query(models.Plan).filter(models.Plan.id == plan_id).first()
                if row:
                    row.content_markdown = full_text
                    session.commit()
            finally:
                session.close()
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/plan/{plan_id}")
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    auth_user: AuthUser = Depends(get_current_user),
):
    from fastapi import HTTPException

    plan = (
        db.query(models.Plan)
        .join(models.User)
        .filter(models.Plan.id == plan_id, models.User.auth_user_id == auth_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {
        "id": plan.id,
        "user_id": plan.user_id,
        "bmi": plan.bmi,
        "bmi_category": plan.bmi_category,
        "bmr": plan.bmr,
        "tdee": plan.tdee,
        "daily_calories": plan.daily_calories,
        "protein_g": plan.protein_g,
        "carbs_g": plan.carbs_g,
        "fat_g": plan.fat_g,
        "water_l": plan.water_l,
        "content_markdown": plan.content_markdown,
        "created_at": plan.created_at,
    }
