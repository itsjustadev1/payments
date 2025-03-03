

class PaymentInfo:
    def __init__(self, uuid: str, transaction_id: str, amount_rub: str, receipt_date: str, event_time: str) -> None:
        self.transaction_id = transaction_id
        self.uuid = uuid  # uuid платежа
        self.amount_rub = amount_rub  # сумма платежа
        self.receipt_date = receipt_date  # дата чека
        self.event_time = event_time  # время платежа


class Payer:
    def __init__(self, account_number: str, bank: str, inn: str, company_name: str, purpose: str) -> None:
        self.account_number = account_number  # номер счета
        self.bank = bank
        self.inn = inn  # инн
        self.company_name = company_name  # наименование компании
        self.purpose = purpose  # цель платежа


def parse_transaction_data(data):
    try:
        payments = []

        for transaction in data:
            event_time = transaction.get('eventTime', '')
            uuid = transaction.get('data', {}).get('uuid', '')
            transaction_id = transaction.get(
                'data', {}).get('transactionId', '')

            # Извлечение amount_rub из amountRub -> amount
            amount_rub = transaction.get('data', {}).get(
                'amountRub', {}).get('amount', 0.0)

            receipt_date = transaction.get('data', {}).get(
                'rurTransfer', {}).get('receiptDate', '')

            payment_info = PaymentInfo(
                uuid=uuid,
                transaction_id=transaction_id,
                amount_rub=str(amount_rub),
                receipt_date=receipt_date,
                event_time=event_time
            )

            payer_data = transaction.get('data', {}).get('rurTransfer', {})
            payer = Payer(
                account_number=payer_data.get('payerAccount', ''),
                bank=payer_data.get('payerBankName', ''),
                inn=payer_data.get('payerInn', ''),
                company_name=payer_data.get('payerName', ''),
                purpose=transaction.get('data', {}).get('paymentPurpose', '')
            )

            payments.append((payment_info, payer))

        return payments
    except Exception as e:
        print(str(e))


