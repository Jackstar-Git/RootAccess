import json
import random
from datetime import date as dt_date
from functools import lru_cache
from typing import List, Dict, Optional, Final, Union
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

def save_quotes(quotes: List[Quote], filepath: str = "data/quotes.json") -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(quotes, f, indent=2, ensure_ascii=False)
        # Clear the cache so next load_quotes call gets fresh data
        load_quotes.cache_clear()
        logger.info(f"Quotes saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save quotes: {e}")
        raise

def get_quote_of_the_day(date_input: Optional[Union[dt_date, str]] = None) -> Quote:
    if date_input is None:
        target_date = dt_date.today()
    elif isinstance(date_input, str):
        target_date = dt_date.fromisoformat(date_input)
    else:
        target_date = date_input

    quotes: List[Quote] = load_quotes()
    num_quotes = len(quotes)
    
    if num_quotes == 0:
        raise ValueError("No quotes available to pick from.")

    abs_day = target_date.toordinal()
    
    cycle_number = abs_day // num_quotes
    day_in_cycle = abs_day % num_quotes
    
    cycle_rng = random.Random(f"cycle_{cycle_number}")
    indices = list(range(num_quotes))
    cycle_rng.shuffle(indices)
    
    selected_index = indices[day_in_cycle]
    return quotes[selected_index]