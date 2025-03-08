from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def form_init_app(app: Flask) -> None:
    csrf.init_app(app)
