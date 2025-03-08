from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from .config import SECRET_KEY, SQLALCHEMY_DATABASE_URI
from .form import form_init_app
from .db import db_init_app
from .login import login_init_app
from .user import user_init_app
from .app import app_init_app
from .sso import sso_init_app
from .navbar import navbars_login

app = Flask(
    __name__,
    # static_folder="static",
    # static_url_path="",
    template_folder="templates"
)

app.secret_key = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

form_init_app(app)
db_init_app(app)
login_init_app(app)
user_init_app(app)
app_init_app(app)
sso_init_app(app)

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("user"))

    return render_template("index.html", navbar_focus="index", navbars=navbars_login)
