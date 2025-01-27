import subprocess
from base64 import b64encode
from typing import List
from card_encryption import encrypt_card
import os

username = os.environ.get("USER") or os.environ.get("USERNAME")
if username == 'itsjustadev':
    prefix = 'outgoing_requests/'
else:
    prefix = ''

# card = '5555555555554444'
# card_number_string = encrypt_card(card).decode('utf-8')


def get_amounts_list(requisite_list: List):
    """
    Возвращает все суммы транзакций в списке
    """
    requisite_list = [item.dict() for item in requisite_list]
    amounts = []
    for item in requisite_list:
        amounts.append(item.get('amount_rub'))
    return amounts


# def make_transaction_body(card, our_account_number, amount_rub, comment):
def make_transaction_body(our_account_number, requisite_list: List, external_id):
    """
    Формирует body для транзакций
    """
    requisite_list = [item.dict() for item in requisite_list]
    requisites = []
    for item in requisite_list:
        card_number_string = encrypt_card(item.get('card')).decode('utf-8')
        new_requisite = {
            "payoutId": item.get('payout_id'),
            "selfemployed": {
                "surname": item.get('surname'),
                "name": item.get('name'),
                "patronymic": item.get('patronymic')
            },
            "payoutRequisite": {
                "payoutType": "CARD",
                "byPan": {
                    "pan": card_number_string,
                    "comment": item.get('comment')
                },
                "payoutTotalAmount": item.get('amount_rub')
            }
        }
        requisites.append(new_requisite)

    request_body = {
        "externalId": external_id,
        "company": {
            "accountNumber": our_account_number,
        },
        "requisite": requisites
    }
    return request_body


# request_body = make_transaction_body(card, our_account_number, '200', 'news')
# json_body = canonicalize(request_body)
# json_data = json.dumps(request_body, separators=(',', ':')).encode()


def create_pkcs7_signature(data, cert_file=prefix+"cert.pem", key_file=prefix+"key.pem"):
    # Записываем данные в файл
    with open("data.json", "wb") as f:
        f.write(data)

    # Формируем команду для подписи PKCS#7
    command = [
        "openssl", "smime", "-sign",
        "-in", "data.json",
        "-signer", cert_file,
        "-inkey", key_file,
        "-outform", "DER",
        "-nodetach",
        "-out", "signature.p7s"
    ]

    # Выполняем команду
    subprocess.run(command, check=True)

    # Читаем подписанный файл и кодируем в Base64
    with open("signature.p7s", "rb") as f:
        signature = f.read()

    return b64encode(signature).decode()


# if __name__ == "__main__":
#     #     data = b'{"amount":1000,"currency":"RUB"}'  # Данные для подписи
#     signature_base64 = create_pkcs7_signature(data=json_data)
#     print("Base64 PKCS#7 Signature:", signature_base64)
