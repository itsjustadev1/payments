from sqlalchemy.future import select
from datetime import datetime


async def is_token_expired(AsyncSessionLocal, model_class):
    """
    Проверяет поле time в таблице Token и сравнивает его с текущим временем.
    :return: True, если прошло более 3300 секунд, либо возникла ошибка, False — если прошло менее 3300 секунд.
    """
    try:
        async with AsyncSessionLocal() as session:
            query = select(model_class).order_by(
                model_class.id.desc()).limit(1)
            result = await session.execute(query)
            token = result.scalars().first()

            if not token or not token.time:
                return True

            time_difference = (datetime.utcnow() - token.time).total_seconds()

            if time_difference <= 3300:
                return False
            else:
                return True

    except Exception as e:
        print(f"Error while checking token: {e}")
        return True


async def insert_or_update_token(AsyncSessionLocal, model_class, **kwargs):
    """
    Универсальная функция для вставки новой записи или обновления существующей в таблице.
    :param model_class: Класс модели таблицы
    :param kwargs: Параметры для полей таблицы
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                query = select(model_class).limit(1)
                result = await session.execute(query)
                existing_record = result.scalars().first()
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
        print(f"An error occurred: {e}")


async def get_refresh_token(AsyncSessionLocal, model_class) -> str:
    """
    Получить refresh_token из таблицы tokens.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: refresh_token если он существует, иначе пустая строка.
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                query = select(model_class.refresh_token)
                result = await session.execute(query)
                refresh_token = result.scalars().first()
                return refresh_token if refresh_token else ""
    except Exception as e:
        print(f"An error occurred while fetching refresh_token: {e}")
        return ""


async def get_access_token(AsyncSessionLocal, model_class) -> str:
    """
    Получить access_token из таблицы tokens.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: access_token если он существует, иначе пустая строка.
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                query = select(model_class.access_token)
                result = await session.execute(query)
                access_token = result.scalars().first()
                return access_token if access_token else ""
    except Exception as e:
        print(f"An error occurred while fetching access_token: {e}")
        return ""
