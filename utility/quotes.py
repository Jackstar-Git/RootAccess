import json
import random
from datetime import date as dt_date
from functools import lru_cache
from utility.logging_utility import logger

@lru_cache(maxsize=1)
def load_quotes(filepath="data/quotes.json"):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [{"text": "Developer failed his job. Quotes are broken :(", "author": "System"}]

def get_quote_of_the_day(date=None):
    if date is None:
        date = dt_date.today()
        logger.info(f"Using today's date for quote of the day: {date}")
    
    quotes = load_quotes()
    seed_str = date.strftime("%Y-%m-%d")
    
    random.seed(seed_str)
    qotd = random.choice(quotes)
    random.seed()
    
    return qotd