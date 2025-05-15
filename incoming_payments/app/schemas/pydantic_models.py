from pydantic import BaseModel
from typing import Optional, List
from pydantic import BaseModel


class BalanceNotFoundResponse(BaseModel):
    message: str


class BalanceResponse(BaseModel):
    balance: str


class IsCompanyResponse(BaseModel):
    exists: bool = True


class IsCompanyNegativeResponse(BaseModel):
    exists: bool = False


class DeleteCompanyResponse(BaseModel):
    success: bool = True


class IncomingTransactionResponse(BaseModel):
    success: bool = True
    all_transactions_unique: bool = True


class DeleteCompanyNegativeResponse(BaseModel):
    success: bool = False


class ReduceBalanceResponse(BaseModel):
    success: bool = True


class ReduceBalanceNegativeResponse(BaseModel):
    success: bool = False


class AddCompanyResponse(BaseModel):
    success: bool = True


class AddCompanyNegativeResponse(BaseModel):
    success: bool = False


class HistoryPaymentItem(BaseModel):
    event_time: Optional[str] = None
    amount_rub: Optional[str] = None


class HistoryPaymentByMonthItem(BaseModel):
    month: str
    amount_rub: str


class AllHistoryPaymentsResponseModel(BaseModel):
    data: Optional[List[HistoryPaymentItem]] = None


class HistoryPaymentsResponseModel(BaseModel):
    last_percent: Optional[float] = 0
    last_price: Optional[float] = 0
    data: Optional[List[HistoryPaymentItem]] = []
    months: Optional[List[HistoryPaymentByMonthItem]] = []


class ReduceBalanceRequest(BaseModel):
    amount_rub: str
    inn: str


class HistoryPaymentsByInnRequest(BaseModel):
    inn: str


class AddCompanyRequest(BaseModel):
    inn: str


class Amount(BaseModel):
    amount: float
    currencyName: str


class DepartmentalInfo(BaseModel):
    uip: str
    drawerStatus101: str
    kbk: str
    oktmo: str
    reasonCode106: str
    taxPeriod107: str
    docNumber108: str
    docDate109: str
    paymentKind110: str


# class RurTransfer(BaseModel):
#     deliveryKind: str
#     departmentalInfo: DepartmentalInfo
#     payeeAccount: str
#     payeeBankBic: str
#     payeeBankCorrAccount: str
#     payeeBankName: str
#     payeeInn: str
#     payeeKpp: str
#     payeeName: str
#     payerAccount: str
#     payerBankBic: str
#     payerBankCorrAccount: str
#     payerBankName: str
#     payerInn: str
#     payerKpp: str
#     payerName: str
#     payingCondition: str
#     purposeCode: str
#     receiptDate: str
#     valueDate: str


# class Data(BaseModel):
#     amount: Amount
#     amountRub: Amount
#     correspondingAccount: str
#     direction: str
#     documentDate: str
#     filial: str
#     number: str
#     operationCode: str
#     operationDate: str
#     paymentPurpose: str
#     priority: str
#     uuid: str
#     transactionId: str
#     debtorCode: str
#     extendedDebtorCode: str
#     rurTransfer: RurTransfer


# class TransactionItem(BaseModel):
#     actionType: str
#     eventTime: str
#     object: str
#     sub: str
#     organizationId: str
#     data: Data

class TransactionItem(BaseModel):
    transaction_id: str
    amount_rub: str
    event_time: str
    inn: str
    company_name: str
