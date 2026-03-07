from datetime import datetime
from typing import List

def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def days_in_month(year: int, month: int) -> int:
    if month in {4, 6, 9, 11}:
        return 30
    if month == 2:
        return 29 if is_leap_year(year) else 28
    return 31

def generate_calendar(year: int, month: int) -> List[List[int]]:
    days: int = days_in_month(year, month)
    first_day_weekday: int = datetime(year, month, 1).weekday()
    
    calendar_matrix: List[List[int]] = []
    week: List[int] = [0] * first_day_weekday
    
    for day in range(1, days + 1):
        week.append(day)
        if len(week) == 7:
            calendar_matrix.append(week)
            week = []
            
    if week:
        week.extend([0] * (7 - len(week)))
        calendar_matrix.append(week)
        
    return calendar_matrix