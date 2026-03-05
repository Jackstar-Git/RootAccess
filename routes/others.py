from flask import Blueprint, render_template
from utility.logging_utility import logger
from utility.quotes import get_quote_of_the_day


others_blueprint = Blueprint("others", __name__)


@others_blueprint.route("/about", methods=["GET", "POST"])
def about():
    logger.info("About route accessed")
    daily_quote = get_quote_of_the_day()
    return render_template("about.jinja-html", quote=daily_quote)


@others_blueprint.route("/contact", methods=["GET", "POST"])
def contact():
    logger.info("Contact route accessed")
    return render_template("contact.jinja-html")


@others_blueprint.route("/imprint", methods=["GET", "POST"])
def imprint():
    logger.info("Imprint route accessed")
    return render_template("imprint.jinja-html")


@others_blueprint.route("/privacy", methods=["GET", "POST"])
def privacy():
    logger.info("Privacy route accessed")
    return render_template("privacy.jinja-html")
