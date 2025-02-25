from service.decimals import check_balance_is_enough, sum_amount
from service.new import *
from schemas.pydantic_models_trans import *
from service.signature_pcks7 import get_amounts_list
from repositories.db_transactions.sql_functions import *
from repositories.db_transactions.token_functions import *
from helper_functions import make_async_request, make_nocert_async_request, update_token
from helper_endpoints import *
from fastapi import FastAPI, APIRouter, HTTPException, Header, Query
from fastapi.responses import Response, JSONResponse
from typing import Optional
import uvicorn
from app_logs.logger import *
from dotenv import load_dotenv

prefix = "/service/v2"
app = FastAPI(docs_url=prefix+"/docs", openapi_url=prefix+"/openapi.json")
load_dotenv()
# адрес для вызова вебхука о пополнении в альфа
WEBHOOK_SERVER = os.getenv('WEBHOOK_SERVER')
PAYOUT_INFO_SERVER = str(os.getenv('PAYOUT_INFO_SERVER'))
TOKEN = os.getenv('TOKEN')
api_router = APIRouter(prefix=prefix)


def authenticate_user(authorization):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    token = authorization.split(" ")[1]
    if token != TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


@api_router.get("/state-payout", response_model=StatePayoutResponse)
async def get_payout_state(request_id: str = Query(..., description="Uuid запроса"), authorization: Optional[str] = Header(None)):
    """
    Эндпоинт для получения информации о транзакции
    """
    authenticate_user(authorization)
    try:
        await update_token()
        access_token = await get_access_token(AsyncSessionLocal, Token)
        header = Headers(authorization=f'Bearer {access_token}', content_type='application/json',
                         accept='application/json')
        response = await make_async_request('get', PAYOUT_INFO_SERVER+request_id, header.get_headers())
        if response:
            return json.loads(response.text)
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return Response(status_code=500)


@api_router.post("/make-webhook", responses={200: {"model": MakeWebhookResponse}, 500: {"model": MakeWebhookResponse}})
async def make_webhook(authorization: Optional[str] = Header(None)):
    """
    Эндпоинт для вызова вебхука
    """
    authenticate_user(authorization)
    try:
        print('------Updating token')
        await update_token()
        access_token = await get_access_token(AsyncSessionLocal, Token)
        print('------Gained token')
        header = Headers(authorization=f'Bearer {access_token}', content_type='application/json',
                         accept='application/json')
        response = await make_async_request('post', WEBHOOK_SERVER, header.get_headers(), data={"object": "ul_transaction_default"})
        if response and response.status_code == 201:
            response_data = MakeWebhookResponse(webhook_done=True)
            return response_data
        else:
            response_data = MakeWebhookResponse(webhook_done=False)
            return JSONResponse(status_code=500, content=response_data.model_dump())
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return Response(status_code=500)


@api_router.post("/make-simple-transaction", responses={200: {"model": MakeTransactionResponse}, 500: {"model": MakeTransactionNegativeResponse}})
async def make_simple_transaction(items: Transactions, authorization: Optional[str] = Header(None)):
    """
    Тестовый пример совершения выплаты физ лицам
    """
    authenticate_user(authorization)
    try:
        our_account_number = '40702810201400022055'
        await update_token()
        access_token = await get_access_token(AsyncSessionLocal, Token)
        header = Headers(authorization=f'Bearer {access_token}', content_type='application/json',
                         accept='application/json')
        response_text = await do_transaction(our_account_number, header, items, None)
        if response_text == 'no_connection':
            return JSONResponse(status_code=500, content={"transaction": "partial_success", "cause": "Транзакция совершена, но счет компании не обновлен"})
        elif response_text:
            response_dict = json.loads(response_text)
            return {"transaction": "yes", **response_dict}
        else:
            return JSONResponse(status_code=500, content={"transaction": "no", "cause": "Ошибка сервера при обработке запроса"})
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return Response(status_code=500)


@api_router.post("/make-transaction", responses={200: {"model": MakeTransactionResponse}, 500: {"model": MakeTransactionNegativeResponse}})
async def make_main_transaction(items: Transactions, authorization: Optional[str] = Header(None)):
    """
    Основная функция для совершения транзакций(выплат физ лицам)
    """
    authenticate_user(authorization)
    try:
        our_account_number = '40702810201400022055'
        await update_token()
        access_token = await get_access_token(AsyncSessionLocal, Token)
        header = Headers(authorization=f'Bearer {access_token}', content_type='application/json',
                         accept='application/json')
        header1 = Headers(authorization=f'Bearer {TOKEN}')
        # проверить баланс, то что он больше чем списание
        response = await make_nocert_async_request('get', f'{SERVER}/balance?inn={items.inn}', header1.get_headers())
        if response and response.status_code == 200:
            data = response.json()
            balance = data.get("balance")
            print(f'\nБаланс компании: {balance}')

        # функция сравнения баланса
            amounts = get_amounts_list(items.transactions)
            summed_amount = sum_amount(amounts)
            print(f'\nОбщая сумма списания: {summed_amount}')
            if check_balance_is_enough(balance, summed_amount):
                # если больше то все ок и делаем транзакцию
                response_text = await do_transaction(our_account_number, header, items, summed_amount)
                if response_text == 'no_connection':
                    return JSONResponse(status_code=500, content={"transaction": "partial_success", "cause": "Транзакция совершена, но счет компании не обновлен"})
                elif response_text:
                    response_dict = json.loads(response_text)
                    return {"transaction": "yes", **response_dict}
        return JSONResponse(status_code=500, content={"transaction": "no", "cause": "Ошибка сервера при обработке запроса"})
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return Response(status_code=500)


async def initialize_and_start_server():
    await update_token()
    # Удаляем и создаём таблицы
    # await drop_all_tables(logger)
    await create_all_tables()
    # Запускаем сервер Uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=8888)
    server = uvicorn.Server(config)
    await server.serve()

app.include_router(api_router)

if __name__ == "__main__":
    asyncio.run(initialize_and_start_server())
