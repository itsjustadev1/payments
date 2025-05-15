import logging
import os

username = os.environ.get("USER") or os.environ.get("USERNAME")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Устанавливаем уровень логирования
# Создаем обработчик для записи логов в файл
if username == 'itsjustadev':
    file_handler = logging.FileHandler("app_logs/app.txt")
else:
    file_handler = logging.StreamHandler()
file_handler.setLevel(logging.INFO)
# Указываем формат для логов
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)
file_handler.setFormatter(formatter)
# Добавляем обработчик к логгеру
logger.addHandler(file_handler)
