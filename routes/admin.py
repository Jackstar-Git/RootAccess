from flask import render_template, request, redirect, url_for, session, Blueprint
from utility.logging_utility import logger
from utility import get_settings

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

#@admin_blueprint.before_request
#def check_login():
#    if "login" not in session and not request.base_url.endswith("login"):
#        logger.warning("User not logged in, redirecting to login page")
#        return redirect(url_for("admin.login"))

@admin_blueprint.route("/login", methods=["GET", "POST"])
def login():
    logger.info("Login route accessed")
    if request.method == "GET":
        logger.info("Rendering login page")
        return render_template("admin/login.jinja-html")

    admin_password = get_settings("admin-password")
    logger.debug(f"Admin password retrieved: {admin_password}")

    if request.form.get("password") != admin_password:
        error = "Passwort ungültig!"
        logger.warning("Invalid password attempt")
        return render_template("admin/login.jinja-html", error=error)

    session.permanent = True
    session["login"] = True
    session.modified = True
    logger.info("User logged in successfully")
    return redirect(url_for("admin.dashboard"))

@admin_blueprint.route("/logout", methods=["GET"])
def logout():
    logger.info("Logout route accessed")
    session.pop("login", None)
    logger.info("User logged out successfully")
    return redirect(url_for("admin.login"))


@admin_blueprint.route("/dashboard", methods=["GET"])
def dashboard():
    logger.info("Dashboard route accessed")
    return render_template("admin/dashboard.jinja-html")