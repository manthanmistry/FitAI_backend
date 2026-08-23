from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import health, calculate, plan, history, progress, report

settings = get_settings()

app = FastAPI(
    title="FitAI API",
    description="AI-powered diet & fitness planning backend.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(health.router, prefix="/api")
app.include_router(calculate.router, prefix="/api")
app.include_router(plan.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(report.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "FitAI API is running. See /docs for API documentation."}
