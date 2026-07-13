from aiogram.fsm.state import StatesGroup, State


class ClientAddition(StatesGroup):
    enter_name = State()      # Название / ФИО
    enter_type = State()      # Тип (ИП, Компания, Физлицо)
    enter_inn = State()       # ИНН (опционально)
    enter_phone = State()     # Телефон (опционально)
    enter_email = State()     # Email (опционально)
    confirm = State()         # Подтверждение
    done = State()            # Результат
