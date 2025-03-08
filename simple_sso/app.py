from flask import Flask, render_template, flash, redirect, url_for, abort, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, URLField, FieldList, FormField, SubmitField
from wtforms.validators import DataRequired, URL
from .login import login_admin_required
from .db_schema import Application, ApplicationRedeemToken
from .db import db
from .navbar import navbars_user, navbars_admin

class ApplicationForm(FlaskForm):
    name = StringField("Application Name", validators=[DataRequired()])
    url = URLField("Redirect URL", validators=[DataRequired(), URL(require_tld=False, allow_ip=True)])
    submit = SubmitField("Create")

class UpdateApplicationForm(FlaskForm):
    name = StringField("Application Name", validators=[DataRequired()])
    url = URLField("Redirect URL", validators=[DataRequired(), URL(require_tld=False, allow_ip=True)])
    submit = SubmitField("Update")

def paginate_query(query, page):
    return query.paginate(page=page, per_page=20, error_out=False)

def app_init_app(app: Flask):
    @app.route("/user/app")
    @login_required
    def user_app():
        navbars = navbars_admin if current_user.is_admin else navbars_user
        page = request.args.get("page", 1, type=int)
        query = request.args.get("query", "")

        apps_query = (
            db.session.query(Application)
                .join(ApplicationRedeemToken, Application.id == ApplicationRedeemToken.application_id)
                .filter(ApplicationRedeemToken.user_id == current_user.id)
                .distinct()
        )

        if query:
            apps_query = apps_query.filter(Application.name.ilike(f"%{query}%"))

        applications = paginate_query(apps_query, page)

        return render_template("app.list.html", navbar_focus="user_app", navbars=navbars, applications=applications, title="Authorized", is_owner=False)

    @app.route("/app/new", methods=["GET", "POST"])
    @login_required
    def app_new():
        form = ApplicationForm()

        if form.validate_on_submit():
            new_app = Application(name=form.name.data, owner_id=current_user.id, url=form.url.data)
            db.session.add(new_app)
            db.session.commit()

            return redirect(url_for("app_info", app_id=new_app.id))

        navbars = navbars_admin if current_user.is_admin else navbars_user

        return render_template("app.new.html", navbar_focus="app_new", navbars=navbars, form=form)

    @app.route("/app/owner")
    @login_required
    def app_owner():
        page = request.args.get("page", 1, type=int)
        query = request.args.get("query", "")
        navbars = navbars_admin if current_user.is_admin else navbars_user

        apps_query = db.session.query(Application).filter(Application.owner_id == current_user.id)
        if query:
            apps_query = apps_query.filter(Application.name.ilike(f"%{query}%"))

        applications = paginate_query(apps_query, page)

        return render_template("app.list.html", navbar_focus="app_owner", navbars=navbars, applications=applications, title="Owned", is_owner=True)

    @app.route("/app/<int:app_id>")
    @login_required
    def app_info(app_id: int):
        app = db.session.query(Application).get(app_id)
        if not app:
            return abort(404)

        navbars = navbars_admin if current_user.is_admin else navbars_user
        is_owner = app.owner_id == current_user.id
        navbar_focus = "app_owner" if is_owner else "admin_app" if current_user.is_admin else "user_app"
        return render_template("app.html", navbar_focus=navbar_focus, navbars=navbars, app=app, is_owner=is_owner, is_admin=current_user.is_admin)

    @app.route("/app/<int:app_id>/setting", methods=["GET", "POST"])
    @login_required
    def app_setting(app_id: int):
        app_ = db.session.query(Application).get(app_id)
        if not app_ or app_.owner_id != current_user.id:
            return abort(403)

        form = UpdateApplicationForm(obj=app_)

        if form.validate_on_submit():
            app_.name = form.name.data
            app_.url = form.url.data
            db.session.commit()

            return redirect(url_for("app_info", app_id=app_.id))

        navbars = navbars_admin if current_user.is_admin else navbars_user
        return render_template("app.setting.html", navbar_focus="app_owner", navbars=navbars, app=app_, form=form, is_owner=True, is_admin=False)

    @app.route("/app/<int:app_id>/delete")
    @login_required
    def app_delete(app_id: int):
        app_ = db.session.query(Application).get(app_id)
        if not app_ or app_.owner_id != current_user.id:
            return abort(403)

        db.session.delete(app_)
        db.session.commit()

        if (next_url := request.args.get("next")) is not None:
            return redirect(next_url)

        return redirect(url_for("admin_app"))

    @app.route("/admin/app")
    @login_required
    @login_admin_required
    def admin_app():
        page = request.args.get("page", 1, type=int)
        query = request.args.get("query", "")

        apps_query = db.session.query(Application)
        if query:
            apps_query = apps_query.filter(Application.name.ilike(f"%{query}%"))

        applications = paginate_query(apps_query, page)

        return render_template("app.list.html", navbar_focus="admin_app", navbars=navbars_admin, applications=applications, title="All", is_owner=False, is_admin=True)

    @app.route("/admin/app/<int:app_id>/setting", methods=["GET", "POST"])
    @login_required
    @login_admin_required
    def admin_app_setting(app_id: int):
        app_ = db.session.query(Application).get(app_id)
        if not app_:
            return abort(404)

        form = UpdateApplicationForm(obj=app_)

        if form.validate_on_submit():
            app_.name = form.name.data
            app_.url = form.url.data
            db.session.commit()

            return redirect(url_for("app_info", app_id=app_.id))

        return render_template("app.setting.html", navbar_focus="admin_app", navbars=navbars_admin, app=app_, form=form, is_owner=False, is_admin=True)

    @app.route("/admin/app/<int:app_id>/delete")
    @login_required
    @login_admin_required
    def admin_app_delete(app_id: int):
        app_ = db.session.query(Application).get(app_id)
        if not app_:
            return abort(404)

        db.session.delete(app_)
        db.session.commit()

        if (next_url := request.args.get("next")) is not None:
            return redirect(next_url)

        return redirect(url_for("admin_app"))
