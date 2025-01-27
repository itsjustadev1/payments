from pydantic import BaseModel
from typing import List
from pydantic.fields import Field


class MakeTransactionResponse(BaseModel):
    transaction: str
    requestId: str
    externalId: str


class MakeTransactionNegativeResponse(BaseModel):
    transaction: str
    cause: str = Field(description='Причина')


class StatePayoutResponse(BaseModel):
    pagination: dict
    requestId: str
    externalId: str
    createdDate: str
    listStatus: str
    error: dict
    statementList: dict


class MakeWebhookResponse(BaseModel):
    webhook_done: bool


class TransactionRequest(BaseModel):
    payout_id: str
    card: str
    surname: str
    name: str
    patronymic: str
    amount_rub: str
    comment: str


class Transactions(BaseModel):
    external_id: str
    inn: str
    transactions: List[TransactionRequest]
