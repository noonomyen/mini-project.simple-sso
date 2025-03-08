from secrets import token_urlsafe
from datetime import datetime
from flask import Flask, render_template, abort, redirect, request
from flask_login import login_required, current_user
from .db_schema import Application, ApplicationRedeemToken, User
from .db import db

def sso_init_app(app: Flask):
    @app.route("/sso/<int:app_id>")
    @login_required
    def sso(app_id: int):
        app_ = db.session.query(Application).get(app_id)
        if not app_:
            return abort(404)

        return render_template("sso.html", app=app_, current_user=current_user)

    @app.route("/sso/<int:app_id>/authorize")
    @login_required
    def sso_authorize(app_id: int):
        app_ = db.session.query(Application).get(app_id)
        if not app_:
            return abort(404)

        token = token_urlsafe(32)
        redeem_token = ApplicationRedeemToken(
            application_id=app_id,
            user_id=current_user.id,
            token=token,
            used=False
        )
        db.session.add(redeem_token)
        db.session.commit()

        return redirect(f"{app_.url}?token={token}")

    @app.route("/sso/<int:app_id>/authorize-deny")
    @login_required
    def sso_authorize_deny(app_id: int):
        app_ = db.session.query(Application).get(app_id)
        if not app_:
            return abort(404)

        return redirect(f"{app_.url}?token=DENY")

    @app.route("/sso/<int:app_id>/redeem")
    def sso_verify(app_id: int):
        token_value = request.args.get("token")
        if not token_value:
            return {"status": "bad_request"}

        token = db.session.query(ApplicationRedeemToken).filter(
            ApplicationRedeemToken.token == token_value,
            ApplicationRedeemToken.application_id == app_id
        ).one_or_none()

        if token is None or token.used or (datetime.now() - token.auth_at).total_seconds() > 60: # type: ignore
            return {"status": "fail"}

        token.used = True # type: ignore
        db.session.commit()

        user = db.session.query(User).get(token.user_id)
        if not user:
            return {"status": "fail"}

        return {
            "status": "success",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "email": user.email
            }
        }
