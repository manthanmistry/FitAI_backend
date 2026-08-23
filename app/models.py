from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth_user_id = Column(Integer, ForeignKey("auth_users.id"), unique=True, index=True, nullable=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    target_weight_kg = Column(Float, nullable=False)

    activity_level = Column(String, nullable=False)
    sleep_hours = Column(Float, nullable=False)
    stress_level = Column(String, nullable=False)
    water_intake_l = Column(Float, nullable=False)

    goal = Column(String, nullable=False)
    workout_experience = Column(String, nullable=False)
    workout_days_per_week = Column(Integer, nullable=False)
    workout_duration_min = Column(Integer, nullable=False)
    workout_location = Column(String, nullable=False)

    diet_type = Column(String, nullable=False)
    allergies = Column(String, default="")
    medical_conditions = Column(String, default="")

    created_at = Column(DateTime, default=datetime.utcnow)

    plans = relationship("Plan", back_populates="user", cascade="all, delete-orphan")
    weight_logs = relationship("WeightLog", back_populates="user", cascade="all, delete-orphan")
    workout_logs = relationship("WorkoutLog", back_populates="user", cascade="all, delete-orphan")
    water_logs = relationship("WaterLog", back_populates="user", cascade="all, delete-orphan")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    bmi = Column(Float)
    bmi_category = Column(String)
    bmr = Column(Float)
    tdee = Column(Float)
    daily_calories = Column(Float)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fat_g = Column(Float)
    water_l = Column(Float)

    content_markdown = Column(Text)  # the full AI generated plan
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="plans")


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weight_kg = Column(Float, nullable=False)
    bmi = Column(Float)
    logged_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="weight_logs")


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity = Column(String, nullable=False)
    duration_min = Column(Integer, nullable=False)
    calories_burned = Column(Float, default=0)
    logged_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workout_logs")


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_l = Column(Float, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="water_logs")
