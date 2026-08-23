"""
Evidence-based health calculations.

BMI: weight(kg) / height(m)^2
BMR: Mifflin-St Jeor equation
TDEE: BMR * activity multiplier
Calories: TDEE adjusted for goal
Macros: split based on goal
"""

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

GOAL_CALORIE_ADJUSTMENT = {
    "weight_loss": -500,
    "muscle_gain": 300,
    "maintenance": 0,
}


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal weight"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    # Mifflin-St Jeor
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender == "male":
        return round(base + 5, 1)
    if gender == "female":
        return round(base - 161, 1)
    # 'other' -> average of male/female offsets
    return round(base - 78, 1)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return round(bmr * multiplier, 1)


def calculate_daily_calories(tdee: float, goal: str) -> float:
    adjustment = GOAL_CALORIE_ADJUSTMENT.get(goal, 0)
    calories = tdee + adjustment
    return round(max(calories, 1200), 1)


def calculate_macros(daily_calories: float, goal: str, weight_kg: float):
    """Returns (protein_g, carbs_g, fat_g)."""
    if goal == "muscle_gain":
        protein_per_kg = 2.0
        fat_pct = 0.25
    elif goal == "weight_loss":
        protein_per_kg = 2.2
        fat_pct = 0.25
    else:
        protein_per_kg = 1.6
        fat_pct = 0.28

    protein_g = round(protein_per_kg * weight_kg, 1)
    protein_cal = protein_g * 4

    fat_cal = daily_calories * fat_pct
    fat_g = round(fat_cal / 9, 1)

    carbs_cal = max(daily_calories - protein_cal - fat_cal, 0)
    carbs_g = round(carbs_cal / 4, 1)

    return protein_g, carbs_g, fat_g


def calculate_water_intake(weight_kg: float, activity_level: str) -> float:
    base_l = weight_kg * 0.033
    if activity_level in ("active", "very_active"):
        base_l += 0.5
    return round(base_l, 1)


def full_calculation(weight_kg, height_cm, age, gender, activity_level, goal):
    bmi = calculate_bmi(weight_kg, height_cm)
    category = bmi_category(bmi)
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    daily_calories = calculate_daily_calories(tdee, goal)
    protein_g, carbs_g, fat_g = calculate_macros(daily_calories, goal, weight_kg)
    water_l = calculate_water_intake(weight_kg, activity_level)

    return {
        "bmi": bmi,
        "bmi_category": category,
        "bmr": bmr,
        "tdee": tdee,
        "daily_calories": daily_calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "water_l": water_l,
    }
