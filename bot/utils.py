from functools import wraps


def check_int(value: str):
    try:
        if int(value) == float(value):
            return True
    except ValueError:
        return False


def check_int_decorator(name: str):
    def wrapper(func):
        @wraps(func)
        async def foo(message, *args, **kwargs):
            if not check_int(message.text):
                await message.reply(f"Неправильный формат, {name} должен быть целым числом.")
                return
            result = await func(message, *args, **kwargs)
            return result

        return foo

    return wrapper
