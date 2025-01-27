from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple
from datetime import datetime
from collections import defaultdict


def calculate_sums(data) -> Tuple[Decimal, Decimal]:
    """
    Функция для расчёта суммы за текущий и предыдущий месяц
    """

    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    # Определяем предыдущий месяц и год
    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    current_month_sum = Decimal(0)
    previous_month_sum = Decimal(0)

    for entry in data:
        event_time = datetime.fromisoformat(
            entry["event_time"].replace("Z", "+00:00"))
        amount = Decimal(entry["amount_rub"])

        # Сравниваем год и месяц
        if event_time.year == current_year and event_time.month == current_month:
            current_month_sum += amount
        elif event_time.year == previous_year and event_time.month == previous_month:
            previous_month_sum += amount

    return current_month_sum, previous_month_sum


def calculate_month_sums(data):
    """
    Функция для расчёта сумм по месяцам
    """

    # Словарь для хранения сумм по месяцам
    monthly_totals = defaultdict(Decimal)

    # Получаем текущий год
    current_year = datetime.now().year

    # Обработка данных
    for item in data:
        # Извлекаем дату из строки
        event_time = datetime.fromisoformat(item['event_time'])
        # Учитываем только данные текущего года
        if event_time.year == current_year:
            month = event_time.month
            # Суммируем платежи для каждого месяца
            monthly_totals[month] += Decimal(item['amount_rub'])

    # Преобразуем результат в требуемый формат и сортируем по месяцам
    result = sorted(
        [{"month": str(month), "amount_rub": str(total)}
         for month, total in monthly_totals.items()],
        key=lambda x: x["month"]
    )
    return result


def convert_to_decimal(number: float | str | Decimal) -> Decimal:
    """
    Преобразует число в Decimal тип, на выходе получаем именно его

    Args:
        number (float | str | Decimal): исходное входное значение

    Raises:
        ValueError: если передано не float,str или Decimal

    Returns:
        Decimal: конвертированное значение
    """
    if not isinstance(number, (float, str, Decimal)):
        raise ValueError
    try:
        if isinstance(number, float):
            return Decimal(str(number))
        if isinstance(number, str):
            return Decimal(number)
        else:
            return Decimal(number)
    except Exception as e:
        raise ValueError(
            f"Ошибка преобразования строки в Decimal: {number}. {e}")


def sum_amount(amount: List[str]) -> str:
    final_result = Decimal(0)
    for item in amount:
        final_result += convert_to_decimal(item)
    return str(final_result)


def add_to_balance(balance: str, number: float | str | Decimal) -> str:
    """
    Прибавляет к балансу новое значение

    Args:
        balance (str): денежная сумма на счету
        number (float | str | Decimal): значение, прибавляемое к балансу

    Raises:
        TypeError: если баланс получен не в строковом представлении,
        либо прибавляемое значение получено не как float, str или Decimal

    Returns:
        str: итоговая конечная сумма баланса и прибавляемого значения
    """
    if not isinstance(balance, str) or not isinstance(number, (float, str, Decimal)):
        raise TypeError
    final_balance = Decimal(balance) + convert_to_decimal(number)
    final_balance = str(final_balance)
    return final_balance


def reduce_balance(balance: str, number: float | str | Decimal) -> str:
    if not isinstance(balance, str) or not isinstance(number, (float, str, Decimal)):
        raise TypeError
    if Decimal(balance) > convert_to_decimal(number):
        final_balance = Decimal(balance) - convert_to_decimal(number)
        final_balance = str(final_balance)
        return final_balance
    else:
        raise ValueError('Value of balance is lower than incoming number')


def check_balance_is_enough(balance: str, number: float | str | Decimal) -> bool:
    if not isinstance(balance, str) or not isinstance(number, (float, str, Decimal)):
        raise TypeError
    decimal_balance = Decimal(balance)
    decimal_number = convert_to_decimal(number)
    return True if decimal_balance > decimal_number else False


# add_to_balance(number)
# decimal_number = Decimal(str(number))
