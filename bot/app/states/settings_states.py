from aiogram.fsm.state import StatesGroup, State


class SettingsUpdate(StatesGroup):
    select_field = State()   # Выбор поля для изменения
    enter_value = State()    # Ввод нового значения
    confirm = State()        # Подтверждение
    done = State()           # Результат
