from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"
    very_active = "very_active"


class StressLevel(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"


class Goal(str, Enum):
    weight_loss = "weight_loss"
    muscle_gain = "muscle_gain"
    maintenance = "maintenance"


class WorkoutExperience(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class WorkoutLocation(str, Enum):
    home = "home"
    gym = "gym"


class DietType(str, Enum):
    vegetarian = "vegetarian"
    vegan = "vegan"
    non_vegetarian = "non_vegetarian"
    eggetarian = "eggetarian"


class UserProfileIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=13, le=100)
    gender: Gender

    height_cm: float = Field(..., ge=50, le=250)
    weight_kg: float = Field(..., ge=20, le=300)
    target_weight_kg: float = Field(..., ge=20, le=300)

    activity_level: ActivityLevel
    sleep_hours: float = Field(..., ge=0, le=24)
    stress_level: StressLevel
    water_intake_l: float = Field(..., ge=0, le=15)

    goal: Goal
    workout_experience: WorkoutExperience
    workout_days_per_week: int = Field(..., ge=1, le=7)
    workout_duration_min: int = Field(..., ge=10, le=240)
    workout_location: WorkoutLocation

    diet_type: DietType
    allergies: Optional[str] = ""
    medical_conditions: Optional[str] = ""

    @field_validator("allergies", "medical_conditions")
    @classmethod
    def clean_text(cls, v):
        return (v or "").strip()[:500]


class CalculationResult(BaseModel):
    bmi: float
    bmi_category: str
    bmr: float
    tdee: float
    daily_calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    water_l: float


class PlanOut(BaseModel):
    id: int
    bmi: Optional[float]
    bmi_category: Optional[str]
    bmr: Optional[float]
    tdee: Optional[float]
    daily_calories: Optional[float]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    water_l: Optional[float]
    content_markdown: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WeightLogIn(BaseModel):
    weight_kg: float = Field(..., ge=20, le=300)


class WorkoutLogIn(BaseModel):
    activity: str = Field(..., min_length=1, max_length=100)
    duration_min: int = Field(..., ge=1, le=600)
    calories_burned: Optional[float] = Field(default=0, ge=0, le=5000)


class WaterLogIn(BaseModel):
    amount_l: float = Field(..., ge=0, le=10)


class ProgressOut(BaseModel):
    weight_logs: List[dict]
    workout_logs: List[dict]
    water_logs: List[dict]
    workout_streak_days: int
