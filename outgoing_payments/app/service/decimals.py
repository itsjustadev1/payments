from decimal import Decimal
from typing import List


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
