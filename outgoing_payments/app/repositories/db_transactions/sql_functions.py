import asyncio
from schemas.sql_entities import *
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
import os
from dotenv import load_dotenv

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


async def create_all_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



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
    except Exception as e:
        print(f"An error occurred: {e}")


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
                else:
                    print(
                        f"No matching records found in {model_class.__tablename__}")
    except Exception as e:
        print(f"An error occurred: {e}")


async def upsert_record(AsyncSessionLocal, model_class, filter_by: dict, **kwargs):
    """
    Универсальная функция для обновления или добавления записи в таблицу.
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
                existing_record = query.scalars().first()

                if existing_record:
                    for key, value in kwargs.items():
                        setattr(existing_record, key, value)
                    print(
                        f"Запись обновлена в таблице {model_class.__tablename__}")
                else:
                    new_record = model_class(**kwargs)
                    session.add(new_record)
                    print(
                        f"Новая запись добавлена в таблицу {model_class.__tablename__}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
