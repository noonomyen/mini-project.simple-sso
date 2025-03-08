from flask import Flask, redirect, url_for, abort, render_template, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Optional
from .navbar import navbars_user, navbars_admin
from .login import login_admin_required
from .db_schema import User
from .db import db
from .login import bcrypt

class UserUpdateForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("E-Mail", validators=[DataRequired(), Email()])

    password = PasswordField("New Password", validators=[Optional()])
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo("password", message="Passwords must match")])

    submit = SubmitField("Save Changes")

def user_init_app(app: Flask):
    @app.route("/user")
    @login_required
    def user():
        navbars = navbars_admin if current_user.is_admin else navbars_user
        return render_template("user.html", admin=False, navbar_focus="user", navbars=navbars, user=current_user)

    @app.route("/user/setting", methods=["GET", "POST"])
    @login_required
    def user_setting():
        navbars = navbars_admin if current_user.is_admin else navbars_user

        if not current_user:
            return abort(404)

        form = UserUpdateForm(obj=current_user)

        if form.validate_on_submit():
            current_user.full_name = form.full_name.data
            current_user.username = form.username.data
            current_user.email = form.email.data

            if form.password.data:
                current_user.password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

            try:
                db.session.commit()
                return redirect(url_for("user"))

            except Exception:
                db.session.rollback()
                flash("Username or email already exists.", "danger")

        return render_template("user.setting.html", navbar_focus="user", navbars=navbars, form=form)

    @app.route("/admin/user")
    @login_required
    @login_admin_required
    def admin_user():
        query = request.args.get("query", "").strip()
        page = request.args.get("page", 1, type=int)

        users_query = db.session.query(
            User.id, User.full_name, User.username, User.email, User.registered_at
        )

        if query:
            users_query = users_query.filter(
                User.full_name.ilike(f"%{query}%") |
                User.username.ilike(f"%{query}%") |
                User.email.ilike(f"%{query}%")
            )

        users = users_query.paginate(page=page, per_page=10, error_out=False) # type: ignore

        return render_template(
            "user.list.html", admin=True, navbar_focus="admin_user",
            navbars=navbars_admin, users=users, query=query
        )

    @app.route("/admin/user/<int:user_id>")
    @login_required
    @login_admin_required
    def admin_user_id(user_id: int):
        user = db.session.query(User).get(user_id)
        if user is None:
            return abort(404)

        return render_template("user.html", admin=True, navbar_focus="admin_user", navbars=navbars_admin, user=user)

    @app.route("/admin/user/<int:user_id>/setting", methods=["GET", "POST"])
    @login_required
    @login_admin_required
    def admin_user_setting(user_id: int):
        user = db.session.query(User).get(user_id)
        if user is None:
            return abort(404)

        form = UserUpdateForm(obj=user)
        if form.validate_on_submit():
            user.full_name = form.full_name.data
            user.username = form.username.data
            user.email = form.email.data

            if form.password.data:
                user.password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

            try:
                db.session.commit()
                return redirect(url_for("admin_user_id", user_id=user.id))

            except Exception:
                db.session.rollback()
                flash("Username or email already exists.", "danger")

        return render_template("user.setting.html", admin=True, navbar_focus="admin_user", navbars=navbars_admin, user=user, form=form)

    @app.route("/admin/user/<int:user_id>/delete")
    @login_required
    @login_admin_required
    def admin_user_del(user_id: int):
        user = db.session.query(User).get(user_id)
        if user is None:
            return abort(404)

        db.session.delete(user)
        db.session.commit()

        if (next_url := request.args.get("next")) is not None:
            return redirect(next_url)

        return redirect(url_for("admin_user"))
