import json
import random
from datetime import date as dt_date
from functools import lru_cache
from typing import List, Dict, Optional, Final
from utility.logging_utility import logger

Quote = Dict[str, str]

DEFAULT_QUOTE: Final[Quote] = {
    "text": "Developer failed his job. Quotes are broken :(",
    "author": "System"
}

@lru_cache(maxsize=1)
def load_quotes(filepath: str = "data/quotes.json") -> List[Quote]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [DEFAULT_QUOTE]

def get_quote_of_the_day(date: Optional[dt_date] = None) -> Quote:
    if date is None:
        date = dt_date.today()
        seed_str: str = date.strftime("%Y-%m-%d")
        logger.info(f"Using today's date for quote of the day: {date}")
    else:
        seed_str: str = date

    quotes: List[Quote] = load_quotes()
    random.seed(seed_str)
    qotd: Quote = random.choice(quotes)
    random.seed()
    
    return qotd