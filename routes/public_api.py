from flask import Blueprint, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utility.logging_utility import logger
from utility.data.quotes import get_quote_of_the_day, load_quotes

public_api_blueprint = Blueprint("public_api", __name__, url_prefix="/api")

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@public_api_blueprint.route("/qotd", methods=["GET"])
@limiter.limit("10 per minute")
def qotd():
    try:
        quote = get_quote_of_the_day()
        return jsonify(quote), 200
    except Exception as e:
        logger.error(f"Error fetching QOTD: {str(e)}")
        return jsonify({"error": "Could not retrieve quote"}), 500

@public_api_blueprint.route("/quotes", methods=["GET"])
@limiter.limit("5 per minute")
def get_all_quotes():
    try:
        quotes = load_quotes()
        return jsonify({
            "count": len(quotes),
            "quotes": quotes
        }), 200
    except Exception as e:
        logger.error(f"Error fetching all quotes: {str(e)}")
        return jsonify({"error": "Could not retrieve quotes list"}), 500