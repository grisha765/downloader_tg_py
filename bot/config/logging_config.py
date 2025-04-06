import logging, os
from config.config import Config

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
        filename = os.path.splitext(os.path.basename(record.pathname))[0]
        return f"{log_color}{record.levelname}{RESET}{WHITE}: {filename}: {message}{RESET}"

class FileFormatter(logging.Formatter):
    def format(self, record):
        record.asctime = self.formatTime(record, self.datefmt)
        filename = os.path.basename(record.pathname)
        message = super().format(record)
        return f"{record.asctime} - {record.levelname}: {filename}:{record.lineno} {message}"

def setup_logging(name='my_app', log_file='/tmp/downloader_tg_py.log'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_formatter = ColoredFormatter('%(message)s')
        stream_handler.setFormatter(stream_formatter)
        stream_handler.setLevel(getattr(logging, Config.log_level, logging.INFO))
        file_handler = logging.FileHandler(log_file)
        file_formatter = FileFormatter('%(message)s')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(getattr(logging, "DEBUG", logging.INFO))
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
    
    return logger

