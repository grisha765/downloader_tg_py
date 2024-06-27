import logging
import os

from config.config import Config 
# Определяем ANSI escape-коды для цветов
RESET = "\x1b[0m"
WHITE = "\x1b[0m"
COLORS = {
    'DEBUG': "\x1b[34m",      # Синий
    'INFO': "\x1b[32m",       # Зеленый
    'WARNING': "\x1b[33m",    # Желтый
    'ERROR': "\x1b[31m",      # Красный
    'CRITICAL': "\x1b[41m",   # Красный фон
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLORS.get(record.levelname, RESET)
        message = super().format(record)
        # Извлечение имени файла без подчеркиваний
        filename = os.path.splitext(os.path.basename(record.pathname))[0]
        return f"{log_color}{record.levelname}{RESET}{WHITE}: {filename}: {message}{RESET}"

def setup_logging(name='my_app'):
    logger = logging.getLogger(name)
    if not logger.handlers:  # Проверяем, есть ли уже обработчики у логгера
        handler = logging.StreamHandler()
        formatter = ColoredFormatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, Config.log_level, logging.INFO))  # Устанавливаем уровень логирования явно
    return logger

