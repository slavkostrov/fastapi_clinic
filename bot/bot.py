import asyncio
import logging
import os
from contextlib import asynccontextmanager

import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states import DogGet, DogPatch, DogPost, DogsGet, TimestampAdd
from utils import check_int_decorator, get_markup_keybord

SERVICE_BASE_URL = "http://app:5555"
WELCOME_MESSAGE = """
    Привет! Это бот для работы с приложением для ветеринарной клиники. Доступные команды:
        - /start
        - /commands"""
        
# TODO: use them from ENUM
AVAILABLE_DOG_KINDS = "terrier", "bulldog", "dalmatian"

@asynccontextmanager
async def make_request(method: str, route: str, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=method,
            url=f"{SERVICE_BASE_URL}/{route}",
            headers={"content-type": "application/json"},
            **kwargs,
        ) as response:
            yield response


logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start welcome message."""
    await message.answer(WELCOME_MESSAGE)


@dp.message(Command("commands"))
async def commands_keyboard(message: types.Message):
    """Message for get all available buttons."""
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Проверить состояние сервиса", callback_data="GET [/]"),
        types.InlineKeyboardButton(text="Добавить Timestamp", callback_data="POST [/post]"),
        types.InlineKeyboardButton(text="Получить информацию о собаках", callback_data="GET [/dog]"),
        types.InlineKeyboardButton(text="Добавить собаку", callback_data="POST [/dog]"),
        types.InlineKeyboardButton(text="Получить информацию о собаке", callback_data="GET [/dog/{pk}]"),
        types.InlineKeyboardButton(text="Изменить информацию о собаке", callback_data="PATCH [/dog/{pk}]")
    )
    builder.adjust(*([1] * 6))
    await message.answer("Выберите действия:", reply_markup=builder.as_markup())


@dp.callback_query(F.data == "GET [/]")
async def check_service_availability_callback(callback: types.CallbackQuery):
    """Callback for checking service availability."""
    async with make_request("GET", "") as response:
        if response.ok:
            await callback.message.answer("Сервис доступен!")
        else:
            await callback.message.answer("Сервис сервис недоступен!")


@dp.callback_query(F.data == "POST [/post]")
async def adding_timestamp_callback(callback: types.CallbackQuery, state: FSMContext):
    """"Callback for add new Timestamp into DB."""
    await state.set_state(TimestampAdd.adding_id)
    await callback.message.answer(text="Введите ID:")


@dp.callback_query(F.data == "POST [/dog]")
async def adding_dog_callback(callback: types.CallbackQuery, state: FSMContext):
    """Callback for add new dog into DB."""
    await state.set_state(DogPost.adding_pk)
    await callback.message.answer(text="Введите PK:")


@dp.callback_query(F.data == "PATCH [/dog/{pk}]")
async def patch_dog_callback(callback: types.CallbackQuery, state: FSMContext):
    """Callback for update existing dog in DB."""
    await state.set_state(DogPatch.adding_pk)
    await callback.message.answer(text="Введите PK:")


@dp.callback_query(F.data == "GET [/dog]")
async def getting_dogs_callback(callback: types.CallbackQuery, state: FSMContext):
    """Callback for getting all dogs by kind."""
    await state.set_state(DogsGet.submitting_kind)
    keyboard = get_markup_keybord(["Все", *AVAILABLE_DOG_KINDS])
    await callback.message.answer(text="Выберите вид:", reply_markup=keyboard)


@dp.callback_query(F.data == "GET [/dog/{pk}]")
async def getting_dog_callback(callback: types.CallbackQuery, state: FSMContext):
    """Callback dog by id."""
    await state.set_state(DogGet.submitting_pk)
    await callback.message.answer(text="Введите PK:")


@dp.message(DogsGet.submitting_kind)
async def get_dogs_by_kind(message: types.Message, state: FSMContext):
    """Return dogs by input kind."""
    url = "dog"
    if message.text != "Все":
        url = f"{url}?kind={message.text}"
    async with make_request("GET", url) as response:
        if response.ok:
            dog_data = await response.json()
            response_message = "Список собак:\n\n"
            for dog in dog_data:
                response_message += f"{dog['pk']}: {dog['name']} ({dog['kind']})\n"
            await message.reply(response_message, reply_markup=types.ReplyKeyboardRemove())
        else:
            error_message = await response.text()
            await message.reply(
                f"Ошибка при получении собаки: {error_message}", reply_markup=types.ReplyKeyboardRemove()
            )
    await state.clear()


@dp.message(DogGet.submitting_pk)
@check_int_decorator("pk")
async def get_dog_by_id(message: types.Message, state: FSMContext):
    """Return dog by input id."""
    async with make_request("GET", f"dog/{int(message.text)}") as response:
        if response.ok:
            dog_data = await response.json()
            await message.answer(f"{dog_data['pk']}: {dog_data['name']} ({dog_data['kind']})")
        else:
            response_text = await response.text()
            await message.answer(f"Ошибка при получении собаки: {response_text}")
    await state.clear()


@dp.message(TimestampAdd.adding_id)
@check_int_decorator("id")
async def adding_id(message: types.Message, state: FSMContext):
    """Add id of timestamp."""
    await state.update_data(id=int(message.text))
    await message.answer(text="Спасибо. Теперь введите timestamp:")
    await state.set_state(TimestampAdd.adding_timestamp)


@dp.message(DogPost.adding_pk)
@check_int_decorator("pk")
async def adding_dog_pk(message: types.Message, state: FSMContext):
    """Add dog's PK."""
    await state.update_data(pk=int(message.text))
    await message.answer(text="Спасибо. Теперь введите имя:")
    await state.set_state(DogPost.adding_name)


@dp.message(DogPost.adding_name)
async def adding_dog_name(message: types.Message, state: FSMContext):
    """Add dog's name"""
    await state.update_data(name=message.text)
    keyboard = get_markup_keybord(AVAILABLE_DOG_KINDS)
    await message.answer(text="Спасибо. Теперь выберите вид:", reply_markup=keyboard)
    await state.set_state(DogPost.adding_kind)


@dp.message(DogPost.adding_kind)
async def adding_new_dog(message: types.Message, state: FSMContext):
    """Adding new dog into DB."""
    await state.update_data(kind=message.text)
    data = await state.get_data()
    async with make_request("POST", "dog", json=data) as response:
        if response.ok:
            await message.answer(f"Добавлена новая собака с параметрами {data}.")
        else:
            response_text = await response.text()
            await message.answer(f"Ошибка при добавлении собаки: {response_text}")
    await state.clear()


@dp.message(DogPatch.adding_pk)
@check_int_decorator("pk")
async def update_dog_pk(message: types.Message, state: FSMContext):
    """Input existing dog's pk."""
    await state.update_data(pk=int(message.text))
    await message.answer(text="Спасибо. Теперь введите имя:")
    await state.set_state(DogPatch.adding_name)


@dp.message(DogPatch.adding_name)
async def updating_dog_name(message: types.Message, state: FSMContext):
    """Update existing dog's name."""
    await state.update_data(name=message.text)
    keyboard = get_markup_keybord(AVAILABLE_DOG_KINDS)
    await message.answer(text="Спасибо. Теперь выберите вид:", reply_markup=keyboard)
    await state.set_state(DogPatch.adding_kind)


@dp.message(DogPatch.adding_kind)
async def updating_dog(message: types.Message, state: FSMContext):
    """Update dog in DB."""
    await state.update_data(kind=message.text)
    data = await state.get_data()
    async with make_request("PATCH", f"dog/{data['pk']}", json=data) as response:
        if response.ok:
            await message.answer(f"Изменена собака с PK {data['pk']} и параметрами {data}.")
        else:
            response_text = await response.text()
            await message.answer(f"Ошибка при обновлении собаки: {response_text}")
    await state.clear()


@dp.message(TimestampAdd.adding_timestamp)
@check_int_decorator("timestamp")
async def adding_timestamp(message: types.Message, state: FSMContext):
    """Adding timestamp in DB."""
    await state.update_data(timestamp=int(message.text))
    data = await state.get_data()
    async with make_request("POST", "post", json=data) as response:
        if response.ok:
            await message.answer(f"Добавлен новый Timestamp с параметрами {data}.")
        else:
            response_text = await response.text()
            await message.answer(f"Ошибка при добавлении Timestamp: {response_text}")
    await state.clear()

@dp.message()
async def unknown_messages_handler(message: types.Message):
    """Handler for unknown messages."""
    await message.answer(WELCOME_MESSAGE)

async def main():
    """Main thread."""
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
