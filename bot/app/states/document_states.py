from aiogram.fsm.state import StatesGroup, State


class DocumentCreation(StatesGroup):
    select_type = State()       # Выбор типа документа (inline)
    select_client = State()     # Выбор клиента (список + "Новый")
    enter_client_name = State() # Ввод названия нового клиента
    enter_items = State()       # Ввод позиций (название, кол-во, цена)
    ask_add_item = State()      # Добавить ещё позицию? (Да/Нет)
    enter_total = State()       # Подтверждение суммы
    enter_date = State()        # Дата документа
    confirm = State()           # Предпросмотр + подтверждение
    done = State()              # Результат (ссылка на PDF)
