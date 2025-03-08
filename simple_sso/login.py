from typing import Optional
from functools import wraps
from flask import Flask, flash, redirect, url_for, render_template, abort, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_bcrypt import Bcrypt
from .db_schema import User
from .db import db
from .navbar import navbars_login

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    full_name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")])
    submit = SubmitField("Register")

login_manager = LoginManager()
bcrypt = Bcrypt()

@login_manager.user_loader
def user_loader(user_id: int) -> Optional[User]:
    return db.session.query(User).get(int(user_id))

@login_manager.unauthorized_handler
def handle_needs_login():
    return redirect(url_for("login", next=request.url))

def login_admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_admin is False:
            return abort(403)

        return func(*args, **kwargs)

    return decorated_view

def login_init_app(app: Flask) -> None:
    login_manager.init_app(app)
    bcrypt.init_app(app)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            user = db.session.query(User).filter_by(username=form.username.data).first()

            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, force=True)

                return redirect(request.args.get("next") or url_for("index"))
            else:
                flash("Invalid username or password.")

        return render_template("login.html", navbar_focus="login", navbars=navbars_login, form=form)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()

        if form.validate_on_submit():
            user = User(
                full_name=form.full_name.data,
                username=form.username.data,
                email=form.email.data,
                is_admin=False,
                password=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            )

            db.session.add(user)

            try:
                db.session.commit()
            except Exception as err:
                flash("Username or email already exists.")
                return redirect(url_for("register"))

            flash("Registered successfully.")
            return redirect(url_for("login"))

        return render_template("register.html", navbar_focus="register", navbars=navbars_login, form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))
