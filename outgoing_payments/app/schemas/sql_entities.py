# - operations(user_info, amount, status)
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Date, DateTime

# Создаем базовый класс для модели
Base = declarative_base()

# Определение модели operations


class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime)
    access_token = Column(String)
    refresh_token = Column(String)
    user_info = Column(String, default='admin')


class Balance(Base):
    __tablename__ = 'balance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_inn = Column(String)
    client_info = Column(String, default='')
    balance = Column(String)


class Operation(Base):
    __tablename__ = 'operations'
    # Поля таблицы
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_info = Column(String, nullable=False)
    sign = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    status = Column(String, nullable=False)


class IncomingPayments(Base):
    __tablename__ = 'incoming_payments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String)
    payer_inn = Column(String)
    payer_name = Column(String)
    operation_date = Column(String)
    amount_rub = Column(String)
