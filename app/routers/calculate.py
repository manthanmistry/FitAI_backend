from fastapi import APIRouter
from app.schemas import UserProfileIn, CalculationResult
from app.calculations import full_calculation

router = APIRouter(tags=["calculate"])


@router.post("/calculate", response_model=CalculationResult)
def calculate(profile: UserProfileIn):
    result = full_calculation(
        weight_kg=profile.weight_kg,
        height_cm=profile.height_cm,
        age=profile.age,
        gender=profile.gender.value,
        activity_level=profile.activity_level.value,
        goal=profile.goal.value,
    )
    return result
