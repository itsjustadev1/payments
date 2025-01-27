import os
from dotenv import load_dotenv
from urllib.parse import quote
from datetime import datetime
from db_transactions.token_functions import get_access_token, get_refresh_token, insert_or_update_token
from db_transactions.sql_functions import *
import httpx
import ssl
# from requests_pkcs12 import get, post

load_dotenv()
CLIENT_ID = str(os.getenv('CLIENT_ID'))
CERTIFICATE_PASSWORD = str(os.getenv('CERTIFICATE_PASSWORD'))
URL = f'https://sandbox.alfabank.ru/oidc/clients/{CLIENT_ID}/client-secret'
URL_FOR_CODE = 'https://id-sandbox.alfabank.ru/oidc/authorize?'
CERTIFICATE_PATH = 'app/certs_alfa/baas_swagger_2025.p12'
AUTHORIZATION_CODE = str(os.getenv('AUTHORIZATION_CODE'))
CLIENT_SECRET = str(os.getenv('CLIENT_SECRET'))
REDIRECT_URI = 'http://localhost'


class Headers:
    def __init__(self, **kwargs):
        # Преобразуем ключи в заглавные буквы
        self.data = {key.replace('_', '-').capitalize()                     : value for key, value in kwargs.items()}

    def get_headers(self) -> dict:
        return self.data


class Body:
    def __init__(self, **kwargs):
        self.data = kwargs

    def generate_body(self) -> str:
        return '&'.join(f'{quote(str(key))}={quote(str(value))}' for key, value in self.data.items())


async def handle_token_response(response, AsyncSessionLocal, model_class):
    """
    Парсит JSON-ответ и сохраняет значения access_token и refresh_token в таблицу.
    :param response: Ответ от сервера, содержащий JSON.
    :param AsyncSessionLocal: Активная сессия базы данных.
    :return: None
    """
    try:
        # Парсим ответ, предполагая, что response.text содержит JSON
        token_data = response.json()

        # Извлекаем токены
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')

        if not access_token or not refresh_token:
            raise ValueError(
                "Missing access_token or refresh_token in response")

        # Обновляем запись в таблице Token
        await insert_or_update_token(AsyncSessionLocal, model_class,
                                     access_token=access_token,
                                     refresh_token=refresh_token,
                                     time=datetime.utcnow())

        print("Токены успешно обновлены.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


# Включение отладки SSL
ssl_context = ssl.create_default_context(
    cafile='certs_alfa/russiantrustedca.pem')
ssl_context.load_cert_chain(
    certfile='certs_alfa/sandbox_cert_2025.cer',
    keyfile='certs_alfa/sandbox_key_2025_unencrypted.key'
)
ssl_context.set_ciphers('ALL')  # Включение всех доступных шифров

# Используйте этот контекст в HTTPX


async def make_nocert_async_request(post_or_get: str, url, headers, data=None):
    """
    Асинхронный HTTP-запрос без проверки сертификатов.
    """
    print('-------async request started')
    async with httpx.AsyncClient(verify=False) as client:
        try:
            if post_or_get.lower() == 'get':
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, json=data, headers=headers)
                print(url)
                print(data if data else "No data for GET request")
                print(headers)
                print(response.text)
            return response
        except Exception as e:
            print(f"Request Error: {e}")
            return None


async def make_async_request(post_or_get: str, url, headers, data=None):
    print('-------async request started')
    async with httpx.AsyncClient(verify=ssl_context) as client:
        try:
            if post_or_get == 'get':
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, json=data, headers=headers)
                print(url)
                print(data)
                print(headers)
                print(response.text)
            return response
        except Exception as e:
            print(f"SSL Error: {e}")


async def make_async_request_payload(post_or_get: str, url, headers, data=None):
    print('-------async request started')
    async with httpx.AsyncClient(verify=ssl_context) as client:
        try:
            if post_or_get == 'get':
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, data=data, headers=headers)
                print(url)
                print(data)
                print(headers)
                print(response.text)
            return response
        except Exception as e:
            print(f"SSL Error: {e}")


async def request_token_alfa(refresh_token):

    try:
        header = Headers(
            content_type='application/x-www-form-urlencoded',
            accept='application/json')
        body = Body(
            grant_type='refresh_token',
            # code=AUTHORIZATION_CODE,
            refresh_token=refresh_token,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
            # redirect_uri=REDIRECT_URI
            # scope='openid signature transactions as-payout',
            # state='abcdef'
        )
        print('формирование запроса на обновление токена')
        print(refresh_token)
        print(CLIENT_ID)
        print(CLIENT_SECRET)

        # payload = f'grant_type=authorization_code&code={AUTHORIZATION_CODE}&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&redirect_uri=http%3A%2F%2Flocalhost&code_verifier=string'
        payload = body.generate_body()
        # data = body.generate_body()
        # encoded_scope = quote(data, safe='')
        final_url = 'https://sandbox.alfabank.ru/oidc/token'
        # final_url = f'https://sandbox.alfabank.ru/oidc/clients/{CLIENT_ID}/client-secret'

        # response = get(final_url, headers=header.get_headers())
        # response = post(final_url,
        #                 data=payload,
        #                 headers=header.get_headers(), verify=False,
        #                 pkcs12_filename=CERTIFICATE_PATH, pkcs12_password=CERTIFICATE_PASSWORD)
        response = await make_async_request_payload('post', final_url, header.get_headers(), payload)
        return response
    except Exception as e:
        print(str(e))

test_accounts = [40702810102300000001, 40702810402300000002,
                 40702810002300000003, 40702978902300000004]


async def create_tables():
    await create_all_tables()


async def update_token():
    print('получение токена из базы')
    refresh_token = await get_refresh_token(AsyncSessionLocal, Token)
    print(f'токен из базы {refresh_token}')
    if not refresh_token:
        refresh_token = str(os.getenv('REFRESH_TOKEN'))
        print('токен из енв: ' + refresh_token)
    response = await request_token_alfa(refresh_token)
    if response:
        print(response.text)
        print(response.status_code)
    await handle_token_response(response, AsyncSessionLocal, Token)


async def request_get_transaction_info(access_token):
    try:
        account_number = 40702810102300000001
        today_date_string = str(datetime.utcnow().date())
        header = Headers(
            authorization=f'Bearer {access_token}',
            accept='application/json')
        url = 'https://sandbox.alfabank.ru/api/statement/transactions'
        additional_url = f'?accountNumber={account_number}&statementDate={today_date_string}'
        final_url = url + additional_url
        response = await make_async_request('get', final_url, header.get_headers())
        return response
    except Exception as e:
        print(str(e))


async def get_transaction_info():
    access_token = await get_access_token(AsyncSessionLocal, Token)
    response = await request_get_transaction_info(access_token)
    if response:
        print(response.text)
        print(response.status_code)


async def main():
    pass
    # await create_tables()         # Создание таблиц
    # await update_token()          # Обновление токена
    # await get_transaction_info()  # Получение информации о транзакциях


if __name__ == "__main__":
    asyncio.run(main())
