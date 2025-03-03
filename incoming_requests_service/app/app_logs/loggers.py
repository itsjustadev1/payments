import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Устанавливаем уровень логирования
# Создаем обработчик для записи логов в файл

file_handler = logging.FileHandler("app_logs/app.txt")
file_handler.setLevel(logging.INFO)
# Указываем формат для логов
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
# Добавляем обработчик к логгеру
logger.addHandler(file_handler)
