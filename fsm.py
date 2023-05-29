from aiogram.dispatcher.filters.state import State, StatesGroup


class AdditionalStep(StatesGroup):
    add_next_message = State()
    add_next_connected_message = State()
    add_list_next_message = State()
    share_list_next_message = State()
