import httpx
import json
from helper_functions import make_async_request, make_async_request_payload, make_nocert_async_request
from signature_pcks7 import create_pkcs7_signature, make_transaction_body
from dotenv import load_dotenv
import os

load_dotenv()

# адрес для запроса к первому сервису
SERVER = os.getenv('SERVER')
TOKEN = os.getenv('TOKEN')


class Headers:
    def __init__(self, **kwargs):
        # Преобразуем ключи в заглавные буквы
        self.data = {key.replace('_', '-').capitalize(): value for key, value in kwargs.items()}

    def get_headers(self) -> dict:
        return self.data


# async def make_async_request(post_or_get: str, url, headers, data=None):
#     print('ENTERING MAKE ASYNC REQUEST')
#     # Передаем клиентский сертификат и закрытый ключ
#     cert = ('certs_alfa/sandbox_cert_2025.cer',
#             'certs_alfa/sandbox_key_2025_unencrypted.key')
#     ca_bundle = 'certs_alfa/russiantrustedca.pem'
#     async with httpx.AsyncClient(verify=ca_bundle, cert=cert) as client:
#         if post_or_get == 'get':
#             response = await client.get(url, headers=headers)
#         else:
#             response = await client.post(url, data=data, headers=headers)
#         return response


async def make_transaction(header: Headers, request_body, signature_encrypted64: str):
    """_summary_

    Args:
        account_number (str): номер счета нашей компании
    """
    api_url = "https://sandbox.alfabank.ru/api/semp/v1/payouts/registries/payouts"  # URL API для выплаты

    # Добавление подписи в запрос
    request_body["digestSignatures"] = [
        {
            "base64Encoded": signature_encrypted64,
            "signatureType": "RSA"
        }
    ]

    # Преобразование JSON в строку
    json_data = json.dumps(request_body, separators=(',', ':')).encode()
    # Отправка POST-запроса в API Альфа-Банка
    response = await make_async_request_payload('post', api_url, header.get_headers(), json_data)
    if response:
        print(response.status_code)
        print(response.text)
    return response


async def do_transaction(our_account_number, header, items, summed_amount):
    print('Entering the do_transaction func')
    try:
        request_body = make_transaction_body(
            our_account_number, items.transactions, items.external_id)
        json_data = json.dumps(request_body, separators=(',', ':')).encode()
        signature = create_pkcs7_signature(json_data)
        response = await make_transaction(header, request_body, signature)
        if response and response.status_code == 200:
            text = response.text
        # если нам нужна простая транзакция без сокращения баланса, то
            if summed_amount == None and response.status_code == 200:
                print(response.status_code)
                print(response.text)
                return text
            elif response.status_code == 200:
                # списываем reduce balance
                header1 = Headers(authorization=f'Bearer {TOKEN}')
                response = await make_nocert_async_request('post', f'{SERVER}/reduce-balance', header1.get_headers(), data={"amount_rub": summed_amount, "inn": items.inn})
                if response and response.status_code == 200:
                    data = response.json()
                    is_reduced = data.get("success")
                    if is_reduced and is_reduced == True:
                        return text
                else:
                    raise ConnectionError('No connection with first service')
        return ''
    except Exception as e:
        print(str(e))
        return 'no_connection'
