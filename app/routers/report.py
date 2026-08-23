from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.pdf_service import generate_report_pdf
from app.auth_models import AuthUser
from app.deps import get_current_user

router = APIRouter(tags=["report"])


@router.get("/download-report")
def download_report(
    plan_id: int = Query(...),
    db: Session = Depends(get_db),
    auth_user: AuthUser = Depends(get_current_user),
):
    plan = (
        db.query(models.Plan)
        .join(models.User)
        .filter(models.Plan.id == plan_id, models.User.auth_user_id == auth_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    user = db.query(models.User).filter(models.User.id == plan.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_dict = {
        "name": user.name, "age": user.age, "gender": user.gender,
        "height_cm": user.height_cm, "weight_kg": user.weight_kg,
        "target_weight_kg": user.target_weight_kg, "goal": user.goal,
        "diet_type": user.diet_type, "activity_level": user.activity_level,
    }
    calc_dict = {
        "bmi": plan.bmi, "bmi_category": plan.bmi_category, "bmr": plan.bmr,
        "tdee": plan.tdee, "daily_calories": plan.daily_calories,
        "protein_g": plan.protein_g, "carbs_g": plan.carbs_g, "fat_g": plan.fat_g,
        "water_l": plan.water_l,
    }

    pdf_bytes = generate_report_pdf(user_dict, calc_dict, plan.content_markdown or "")

    filename = f"FitAI-Report-{user.name.replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
