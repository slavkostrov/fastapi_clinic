from aiogram.fsm.state import State, StatesGroup


class TimestampAdd(StatesGroup):
    adding_id = State()
    adding_timestamp = State()


class DogGet(StatesGroup):
    submitting_pk = State()


class DogsGet(StatesGroup):
    submitting_kind = State()


class DogPost(StatesGroup):
    adding_pk = State()
    adding_name = State()
    adding_kind = State()


class DogPatch(StatesGroup):
    adding_pk = State()
    adding_name = State()
    adding_kind = State()
