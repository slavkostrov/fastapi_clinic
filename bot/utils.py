import typing as tp
from functools import wraps
from aiogram import types

def check_int(value: str):
    try:
        if int(value) == float(value):
            return True
    except ValueError:
        return False


def check_int_decorator(name: str) -> tp.Callable:

    def wrapper(func: tp.Callable) -> tp.Callable:

        @wraps(func)
        async def foo(message: types.Message, *args, **kwargs) -> tp.Any:
            if not check_int(message.text):
                await message.reply(f"Неправильный формат, {name} должен быть целым числом.")
                return
            result = await func(message, *args, **kwargs)
            return result

        return foo

    return wrapper

def get_markup_keybord(options: tp.List[str]) -> types.ReplyKeyboardMarkup:
    """Создает клавиатуру на основе доступных опций."""
    kb = [[types.KeyboardButton(text=option)] for option in options]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    return keyboard 
