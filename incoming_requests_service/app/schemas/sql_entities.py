from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

# Создаем базовый класс для модели
Base = declarative_base()


class Companies(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    inn = Column(
        String,
        unique=True,
        nullable=False
    )


class Balance(Base):
    __tablename__ = 'balance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_inn = Column(String)
    balance = Column(String)
    client_info = Column(String, default='')


class LiteIncomingPayments(Base):
    __tablename__ = 'lite_incoming_payments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String)
    amount_rub = Column(String)
    event_time = Column(String)
    inn = Column(String)
    company_name = Column(String)

    def to_history_payments(self):
        return {
            "inn": self.inn,
            "event_time": self.event_time,
            "amount_rub": self.amount_rub
        }


# class IncomingPayments(Base):
#     __tablename__ = 'incoming_payments'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     transaction_id = Column(String)
#     uuid = Column(String)
#     amount_rub = Column(String)
#     receipt_date = Column(String)
#     event_time = Column(String)
#     account_number = Column(String)
#     bank = Column(String)
#     inn = Column(String)
#     company_name = Column(String)
#     purpose = Column(String)

#     def to_history_payments(self):
#         return {
#             "inn": self.inn,
#             "event_time": self.event_time,
#             "amount_rub": self.amount_rub
#         }

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "transaction_id": self.transaction_id,
#             "uuid": self.uuid,
#             "amount_rub": self.amount_rub,
#             "receipt_date": self.receipt_date,
#             "event_time": self.event_time,
#             "account_number": self.account_number,
#             "bank": self.bank,
#             "inn": self.inn,
#             "company_name": self.company_name,
#             "purpose": self.purpose
#         }
