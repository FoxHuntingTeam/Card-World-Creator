import logging
import traceback
from functools import wraps

log_file = "Loger.txt"

def error_logger():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Ініціалізація логгера
                logger = logging.getLogger(func.__module__)
                logger.setLevel(logging.ERROR)

                # Налаштування обробника файлу
                handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)

                logger.error(f'Exception occurred in {func.__name__}: {str(e)}\n{traceback.format_exc()}')

                raise

        return wrapper
    return decorator
