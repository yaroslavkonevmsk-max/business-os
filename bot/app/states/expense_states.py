from aiogram.fsm.state import StatesGroup, State


class ExpenseAddition(StatesGroup):
    enter_amount = State()       # Ввод суммы
    select_category = State()    # Выбор категории (inline)
    enter_description = State()  # Описание (опционально)
    confirm = State()            # Подтверждение
    done = State()               # Результат + обновление налога
