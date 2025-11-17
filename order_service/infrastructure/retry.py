"""
Утилиты для retry механизмов
"""
import asyncio
import logging
from typing import Callable, TypeVar, Optional
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


async def retry_async(
    func: Callable[..., T],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    *args,
    **kwargs
) -> T:
    """
    Retry механизм для асинхронных функций
    
    Args:
        func: Асинхронная функция для выполнения
        max_attempts: Максимальное количество попыток
        delay: Начальная задержка между попытками (секунды)
        backoff: Множитель для увеличения задержки
        exceptions: Кортеж исключений, при которых нужно повторять
        *args, **kwargs: Аргументы для функции
        
    Returns:
        Результат выполнения функции
        
    Raises:
        Последнее исключение, если все попытки исчерпаны
    """
    current_delay = delay
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts:
                logger.warning(
                    f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                    f"Retrying in {current_delay}s..."
                )
                await asyncio.sleep(current_delay)
                current_delay *= backoff
            else:
                logger.error(
                    f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                )
    
    raise last_exception


def retry_decorator(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Декоратор для добавления retry механизма к асинхронным функциям
    
    Usage:
        @retry_decorator(max_attempts=5, delay=2.0)
        async def my_function():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_async(
                func,
                max_attempts=max_attempts,
                delay=delay,
                backoff=backoff,
                exceptions=exceptions,
                *args,
                **kwargs
            )
        return wrapper
    return decorator

