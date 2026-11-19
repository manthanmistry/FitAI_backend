import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()
database_url = settings.sqlalchemy_database_url

if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif "render.com" in database_url:
    connect_args = {"sslmode": "require", "gssencmode": "disable"}
else:
    connect_args = {}

engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app import models, auth_models  # noqa: F401  ensure models are registered
    last_error = None
    for attempt in range(5):
        try:
            Base.metadata.create_all(bind=engine)
            _migrate_sqlite()
            return
        except OperationalError as exc:
            last_error = exc
            time.sleep(2 + attempt)
    raise last_error


def _migrate_sqlite():
    if not database_url.startswith("sqlite"):
        return
    with engine.begin() as conn:
        tables = {
            row[0]
            for row in conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
        }
        if "users" not in tables:
            return
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
        if cols and "auth_user_id" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN auth_user_id INTEGER"))
