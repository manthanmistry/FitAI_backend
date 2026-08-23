"""
Handles all communication with the Groq API.
The API key is read from the backend environment only and is never
sent to, or exposed through, the frontend.
"""

from openai import OpenAI
from app.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """
You are FitAI, an AI fitness and nutrition assistant.

Provide safe, personalized fitness and nutrition recommendations.

Always include:

- Weekly Overview
- Workout Schedule (Markdown table)
- 7-Day Meal Plan (Markdown table)
- Macronutrient Breakdown
- Recovery & Sleep Advice
- Weekly Goals
- Motivation Tips
- Medical Disclaimer

Use proper Markdown headings, tables and bullet points.
"""


def _client() -> OpenAI:
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(
        api_key=settings.openai_api_key,
        base_url="https://api.groq.com/openai/v1",
    )


def build_user_prompt(profile: dict, calc: dict) -> str:
    return f"""
Create a complete personalized fitness and nutrition plan.

## User Profile

- Name: {profile.get("name","")}
- Age: {profile.get("age","")}
- Gender: {profile.get("gender","")}
- Height: {profile.get("height_cm","")} cm
- Weight: {profile.get("weight_kg","")} kg
- Target Weight: {profile.get("target_weight_kg","")} kg
- Goal: {profile.get("goal","")}
- Activity Level: {profile.get("activity_level","")}
- Workout Experience: {profile.get("workout_experience","")}
- Workout Days Per Week: {profile.get("workout_days_per_week","")}
- Workout Duration: {profile.get("workout_duration_min","")} minutes
- Workout Location: {profile.get("workout_location","")}
- Diet Type: {profile.get("diet_type","")}
- Allergies: {profile.get("allergies") or "None"}
- Medical Conditions: {profile.get("medical_conditions") or "None"}
- Sleep: {profile.get("sleep_hours","")} hours
- Stress Level: {profile.get("stress_level","")}

## Health Metrics

- BMI: {calc.get("bmi","")} ({calc.get("bmi_category","")})
- BMR: {calc.get("bmr","")} kcal/day
- TDEE: {calc.get("tdee","")} kcal/day
- Daily Calories: {calc.get("daily_calories","")} kcal/day
- Protein: {calc.get("protein_g","")} g/day
- Carbohydrates: {calc.get("carbs_g","")} g/day
- Fat: {calc.get("fat_g","")} g/day
- Water: {calc.get("water_l","")} L/day

Generate the response using Markdown.

## Weekly Overview

Explain the overall strategy.

## Workout Schedule

Create a weekly workout schedule as a Markdown table with:

| Day | Workout | Exercises | Sets/Reps | Duration |

The workout must match the user's goal, experience level, workout days and workout location.

## 7-Day Meal Plan

Create a Markdown table with:

| Day | Breakfast | Lunch | Dinner | Snacks |

Match the user's diet preference and allergies.

## Macronutrient Breakdown

Explain why the calorie and macro targets are suitable.

## Recovery & Sleep Advice

Provide personalized recovery advice.

## Weekly Goals

Give 5 measurable goals.

## Motivation Tips

Provide encouraging but realistic advice.

## Disclaimer

Advise consulting a healthcare professional before starting a new exercise or nutrition plan.
"""


def stream_plan(profile: dict, calc: dict):
    client = _client()

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": build_user_prompt(profile, calc),
            },
        ],
        temperature=0.7,
        max_tokens=2500,
        stream=True,
    )

    for chunk in response:
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta

        if delta and delta.content:
            yield delta.content
