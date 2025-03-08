from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .db_schema import Base

__all__ = ["db_init_app", "db_create_all", "db"]

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

def db_init_app(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)

def db_create_all() -> None:
    db.create_all()
