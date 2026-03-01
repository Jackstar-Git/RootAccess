import json
import os
import re
import time
from datetime import datetime, timedelta

from flask import render_template_string, request, jsonify, abort, session, Blueprint, send_file, render_template, redirect, url_for

from FlaskClass import csrf, app
from logging_utility import logger
from utility import get_settings, is_valid_json, get_product_by_id, sanitize_path, get_products, convert_markdown_to_html, get_coupons, get_coupon_by_id, generate_calendar, get_events, query_events, add_product, add_coupon, get_contact_requests, get_contact_by_id, get_event_by_id, get_orders, get_order_by_id

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

#===========================
# Authentication Functions
#===========================

# This function checks if the user is logged in before processing any request
@admin_blueprint.before_request
def check_login():
    if ("login" not in session) and (not request.base_url.endswith("login")):
        logger.warning("User not logged in, redirecting to login page")
        return redirect(url_for("admin.login"))

# This function handles the login process
@admin_blueprint.route("/login", methods=["GET", "POST"])
def login():
    logger.info("Login route accessed")
    if request.method == "GET":
        logger.info("Rendering login page")
        return render_template("admin/login.jinja-html")

    admin_password: dict = get_settings("admin-password")
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

# This function handles the logout process
@admin_blueprint.route("/logout", methods=["GET"])
def logout():
    logger.info("Logout route accessed")
    session.pop("login")
    logger.info("User logged out successfully")
 