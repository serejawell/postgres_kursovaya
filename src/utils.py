
def filter_salary(salary: dict) -> float | None:
    """
    Функция для фильтрации зарплаты.
    """
    if salary is not None:
        if salary['from'] is not None and salary['to'] is not None:
            return round((salary['from'] + salary['to']) / 2)
        elif salary['from'] is not None:
            return salary['from']
        elif salary['to'] is not None:
            return salary['to']
    return None