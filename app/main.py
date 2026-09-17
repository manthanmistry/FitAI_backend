from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import health, calculate, plan, history, progress, report, auth

settings = get_settings()

app = FastAPI(
    title="FitAI API",
    description="AI-powered diet & fitness planning backend.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost",
        "https://fit-ai-frontend-three.vercel.app",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(calculate.router, prefix="/api")
app.include_router(plan.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(report.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "FitAI API is running. See /docs for API documentation."}