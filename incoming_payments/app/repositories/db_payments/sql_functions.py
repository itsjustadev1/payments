import asyncio
import decimal
from schemas.sql_entities import *
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
import os
from dotenv import load_dotenv
from decimals import add_to_balance, reduce_balance
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import MetaData


load_dotenv()
username = str(os.getenv('POSTGRES_USER'))
password = str(os.getenv('POSTGRES_PASSWORD'))
host = str(os.getenv('HOST'))
port = str(os.getenv('PORT'))
database = str(os.getenv('POSTGRES_DB'))
DATABASE_URL = f'postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}'
async_engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False)


async def insert_record(AsyncSessionLocal, model_class, **kwargs):
    """
    Универсальная функция для добавления записи в таблицу.
    :param model_class: Класс модели таблицы
    :param kwargs: Параметры для полей таблицы
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                new_record = model_class(**kwargs)
                session.add(new_record)

        print(f"Новая запись добавлена в таблицу {model_class.__tablename__}")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


async def create_all_tables(logger):
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Таблицы успешно созданы.")
    except Exception as e:
        logger.error("Ошибка при создании таблиц: %s", e)


async def drop_all_tables(logger):
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Таблицы успешно удалены.")
    except Exception as e:
        logger.error("Ошибка при создании таблиц: %s", e)



async def select_records(AsyncSessionLocal, model_class, **filter_kwargs):
    """
    Универсальная функция для выборки записей из таблицы.
    :param AsyncSessionLocal: Асинхронный класс сессии
    :param model_class: Класс модели таблицы
    :param filter_kwargs: Параметры фильтрации (field=value)
    :return: Список найденных записей
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                query = select(model_class)
                if filter_kwargs:
                    query = query.filter_by(**filter_kwargs)
                result = await session.execute(query)
                records = result.scalars().all()
        print(
            f"Найдено {len(records)} записей в таблице {model_class.__tablename__}")
        return records
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


async def insert_payment(AsyncSessionLocal, model_class, unique_field: str, **kwargs):
    """
    Универсальная функция для добавления записи в таблицу с проверкой на дубликаты.
    :param model_class: Класс модели таблицы
    :param unique_field: Название поля, по которому проверяем уникальность
    :param kwargs: Параметры для полей таблицы
    """
    is_unique_transaction = 0
    unique_value = kwargs.get(unique_field)

    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                if unique_value is not None:
                    query = select(model_class).filter(
                        getattr(model_class, unique_field) == unique_value
                    )
                    result = await session.execute(query)
                    existing_record = result.scalar_one_or_none()

                    if existing_record:
                        print(
                            f"Запись с {unique_field}={unique_value} уже существует. Вставка не требуется.")
                    else:
                        new_record = model_class(**kwargs)
                        session.add(new_record)
                        print(
                            f"Новая запись добавлена в таблицу {model_class.__tablename__}")
                        is_unique_transaction = 1
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        finally:
            return True if is_unique_transaction else False


async def delete_one_record(AsyncSessionLocal, model_class, **filters):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                query = select(model_class).filter_by(**filters).limit(1)
                result = await session.execute(query)
                first_record = result.scalars().first()
                if first_record:
                    await session.delete(first_record)
                    await session.commit()
                    print(
                        f"Record with {filters} deleted successfully from {model_class.__tablename__}")
                    return True
                else:
                    print(
                        f"No matching records found in {model_class.__tablename__}")
                    return False
    except Exception as e:
        print(f"An error occurred: {e}")


async def upsert_balance(AsyncSessionLocal, amount_rub: str | float | decimal.Decimal, inn: str, company_name: str):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                query = await session.execute(select(Balance).filter_by(client_inn=inn))
                record = query.scalars().first()

                if record:
                    record.balance = add_to_balance(record.balance, amount_rub)
                else:
                    new_record = Balance(
                        client_inn=inn, balance=amount_rub, client_info=company_name)
                    session.add(new_record)
    except Exception as e:
        print(str(e))


async def reducing_balance(AsyncSessionLocal, amount_rub: str | float | decimal.Decimal, inn: str):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                query = await session.execute(select(Balance).filter_by(client_inn=inn))
                record = query.scalars().first()
                if record:
                    record.balance = reduce_balance(record.balance, amount_rub)
                    return True
    except Exception as e:
        print(str(e))


async def select_balance(AsyncSessionLocal, inn: str):
    returning_value = None
    try:
        async with AsyncSessionLocal() as session:
            query = await session.execute(select(Balance).filter_by(client_inn=inn))
            record = query.scalars().first()

            if record:
                returning_value = record.balance
            else:
                print('Выбрать баланс не удалось')
    except Exception as e:
        print(str(e))
    finally:
        return returning_value


async def hard_upsert_balance(AsyncSessionLocal, amount_rub: str, model_class: Balance, filter_by: dict, **kwargs):
    """
    Универсальная функция для обновления или добавления баланса.
    :amount_rub: Пришедшая сумма в рублях
    :param model_class: Класс модели таблицы
    :param filter_by: Словарь с параметрами для фильтрации записи
    :param kwargs: Параметры для полей таблицы
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                query = await session.execute(
                    select(model_class).filter_by(**filter_by)
                )
                record = query.scalars().first()

                if record:
                    record.balance = add_to_balance(record.balance, amount_rub)
                    print(
                        f"Баланс компании {filter_by} обновлен в таблице {model_class.__tablename__}")
                else:
                    new_record = model_class(**kwargs)
                    session.add(new_record)
                    print(
                        f"Новая комания и ее баланс добавлен в таблицу {model_class.__tablename__}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
