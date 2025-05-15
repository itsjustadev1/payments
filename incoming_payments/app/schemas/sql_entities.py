from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

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