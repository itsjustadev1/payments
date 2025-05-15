import subprocess
from base64 import b64encode
from typing import List
from service.card_encryption import encrypt_card



def get_amounts_list(requisite_list: List):
    """
    Возвращает все суммы транзакций в списке
    """
    requisite_list = [item.dict() for item in requisite_list]
    amounts = []
    for item in requisite_list:
        amounts.append(item.get('amount_rub'))
    return amounts


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


def create_pkcs7_signature(data, cert_file="cert.pem", key_file="key.pem"):
    with open("data.json", "wb") as f:
        f.write(data)

    command = [
        "openssl", "smime", "-sign",
        "-in", "data.json",
        "-signer", cert_file,
        "-inkey", key_file,
        "-outform", "DER",
        "-nodetach",
        "-out", "signature.p7s"
    ]

    subprocess.run(command, check=True)

    with open("signature.p7s", "rb") as f:
        signature = f.read()

    return b64encode(signature).decode()