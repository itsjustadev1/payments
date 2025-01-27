from enum import unique
import os
import json
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, APIRouter, Query
from fastapi.responses import Response, JSONResponse
from decimals import *
from pydantic_models import *
from db_payments.sql_entities import *
from db_payments.sql_functions import *
from request_entities import *
from app_logs.loggers import *
from time_checker import *


prefix = "/service/v1"
app = FastAPI(docs_url=prefix+"/docs", openapi_url=prefix+"/openapi.json")
load_dotenv()
TOKEN = os.getenv('TOKEN')
api_router = APIRouter(prefix=prefix)


def authenticate_user(authorization):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    token = authorization.split(" ")[1]
    if token != TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


def parsing_records(records):
    final_result = []
    if not records:
        return []
    else:
        for record in records:
            final_result.append(record.to_history_payments())
        return final_result


@api_router.get("/history-payments", response_model=HistoryPaymentsResponseModel)
async def get_history_payments(inn: str = Query(..., description="ИНН компании"), full_year: bool = Query(False, description="Фильтр данных за весь год"), authorization: Optional[str] = Header(None)):
    """
    Получение истории зачислений на счет компании по инн
    """
    authenticate_user(authorization)
    try:
        records = await select_records(AsyncSessionLocal, LiteIncomingPayments, inn=inn)
        result = parsing_records(records)
        if not result:
            return JSONResponse(status_code=404, content=HistoryPaymentsResponseModel().model_dump())
        if isinstance(result, list):
            # фильтрация либо по полгода либо по году
            time_distance = six_months_ago if not full_year else one_year_ago
            results_list = [{k: v for k, v in entry.items() if k != "inn"}
                            for entry in result if convert_to_datetime(entry["event_time"]) >= time_distance]
            current_month_sum, previous_month_sum = calculate_sums(
                results_list)
            all_month_sums = calculate_month_sums(results_list)
            result = HistoryPaymentsResponseModel(
                # процент зачислений текущий/прошлый месяц
                last_percent=(current_month_sum / previous_month_sum).quantize(Decimal(
                    '0.01'), rounding=ROUND_HALF_UP) if previous_month_sum else Decimal('1.00'),
                # общая сумма зачислений в этом месяце
                last_price=current_month_sum,
                data=results_list,
                months=all_month_sums
            )
        return result
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return JSONResponse(content=[], status_code=500)


@api_router.get("/all-history-payments", response_model=AllHistoryPaymentsResponseModel)
async def get_all_history_payments(authorization: Optional[str] = Header(None)):
    """
    Получение истории зачислений на счет всех компаний
    """
    authenticate_user(authorization)
    try:
        records = await select_records(AsyncSessionLocal, LiteIncomingPayments)
        returning_value = parsing_records(records)
        result = AllHistoryPaymentsResponseModel(
            data=returning_value
        )
        return result
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return JSONResponse(content=[], status_code=500)


@api_router.get("/balance", responses={200: {"model": BalanceResponse}, 404: {"model": BalanceNotFoundResponse}})
async def get_company_balance(inn: str = Query(..., description="ИНН компании"), authorization: Optional[str] = Header(None)):
    """
    Получение баланса компании по инн
    """
    authenticate_user(authorization)
    try:
        balance = await select_balance(AsyncSessionLocal, inn=inn)
        company = await select_records(AsyncSessionLocal, Companies, inn=inn)
        if balance is None and not company:
            response_data = BalanceNotFoundResponse(
                message="Компания не найдена")
            return JSONResponse(status_code=404, content=response_data.model_dump())
        elif balance is None and company:
            response_data = BalanceResponse(balance="0.0")
            return response_data
        else:
            response_data = BalanceResponse(balance=balance)
            return response_data
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return JSONResponse(content=[], status_code=500)


@api_router.post("/add-company", responses={200: {"model": AddCompanyResponse}, 500: {"model": AddCompanyNegativeResponse}})
async def add_company(item: AddCompanyRequest, authorization: Optional[str] = Header(None)):
    """
    Добавление новой компании в базу
    """
    authenticate_user(authorization)
    try:
        result = await insert_record(AsyncSessionLocal, Companies, inn=item.inn)
        if result:
            response_data = AddCompanyResponse(success=True)
            return response_data
        else:
            response_data = AddCompanyResponse(success=False)
            return JSONResponse(status_code=500, content=response_data.model_dump())
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return JSONResponse(content=[], status_code=500)


@api_router.get("/company", responses={200: {"model": IsCompanyResponse}, 404: {"model": IsCompanyNegativeResponse}})
async def is_company(inn: str = Query(..., description="ИНН компании"), authorization: Optional[str] = Header(None)):
    """
    Проверка существования компании в базе
    """
    authenticate_user(authorization)
    try:
        records = await select_records(AsyncSessionLocal, Companies, inn=inn)
        if records:
            response_data = IsCompanyResponse(exists=True)
            return response_data
        else:
            response_data = IsCompanyResponse(exists=False)
            return JSONResponse(status_code=404, content=response_data.model_dump())
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return JSONResponse(content=[], status_code=500)


@api_router.delete("/company", responses={200: {"model": DeleteCompanyResponse}, 500: {"model": DeleteCompanyNegativeResponse}})
async def delete_company(inn: str = Query(..., description="ИНН компании"), authorization: Optional[str] = Header(None)):
    """
    Удаление компании из базы
    """
    authenticate_user(authorization)
    try:
        result = await delete_one_record(AsyncSessionLocal, Companies, inn=inn)
        if result:
            response_data = DeleteCompanyResponse(success=True)
            return response_data
        else:
            response_data = DeleteCompanyResponse(success=False)
            return JSONResponse(status_code=500, content=response_data.model_dump())
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return JSONResponse(content=[], status_code=500)


@api_router.post("/reduce-balance", responses={200: {"model": ReduceBalanceResponse}, 500: {"model": ReduceBalanceNegativeResponse}})
async def reduce_company_balance(item: ReduceBalanceRequest, authorization: Optional[str] = Header(None)):
    """
    Вычет со счета компании после совершения выплаты физ лицам
    """
    authenticate_user(authorization)
    try:
        is_reduced = await reducing_balance(AsyncSessionLocal, item.amount_rub, item.inn)
        if is_reduced:
            response_data = ReduceBalanceResponse(success=True)
            return response_data
        else:
            response_data = ReduceBalanceResponse(success=False)
            return JSONResponse(status_code=500, content=response_data.model_dump())
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return JSONResponse(content=[], status_code=500)


@api_router.post("/incoming-transaction")
async def test(item: List[TransactionItem]):
    """
    Прием данных о полученной транзакции на счет компании
    """
    serialized_data = json.dumps(
        [transaction.dict() for transaction in item], ensure_ascii=False, indent=4)
    logger.info(f"{serialized_data}\n\n\n")
    unique_flag = True
    try:
        for _ in item:
            is_unique_transaction = await insert_payment(AsyncSessionLocal, LiteIncomingPayments, unique_field='transaction_id', transaction_id=_.transaction_id, amount_rub=str(_.amount_rub), event_time=_.event_time, inn=_.inn, company_name=_.company_name)
            if is_unique_transaction:
                await upsert_balance(AsyncSessionLocal, str(_.amount_rub), _.inn, company_name=_.company_name)
            else:
                unique_flag = False
        return IncomingTransactionResponse(
            success=True, all_transactions_unique=unique_flag)
    except Exception as e:
        logger.info('\n\nERROR'+str(e)+'\n\n')
        return JSONResponse(content=[], status_code=500)


async def initialize_and_start_server():
    # Удаляем и создаём таблицы
    # await drop_all_tables(logger)
    await create_all_tables(logger)
    # Запускаем сервер Uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=8080)
    server = uvicorn.Server(config)
    await server.serve()


app.include_router(api_router)


if __name__ == "__main__":
    asyncio.run(initialize_and_start_server())
