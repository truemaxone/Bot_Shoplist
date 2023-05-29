from aiogram import types
from bot import db


def get_main_kb():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Показать списки")
    btn2 = types.KeyboardButton("Добавить список")
    btn3 = types.KeyboardButton("Добавить продукты")
    btn4 = types.KeyboardButton("Удалить список")
    btn5 = types.KeyboardButton("Поделиться списком")
    keyboard.add(btn1, btn2, btn3, btn4, btn5)
    return keyboard


def get_show_kb():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(text='⬅', callback_data='back')
    btn2 = types.InlineKeyboardButton(text='✏', callback_data='delete')
    keyboard.add(btn1, btn2)
    return keyboard


def get_del_list_kb():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(text='✔', callback_data='delete_list_yes')
    btn2 = types.InlineKeyboardButton(text='✖', callback_data='delete_list_no')
    keyboard.add(btn1, btn2)
    return keyboard


def get_inline_lists_kb(list_of_titles, message):
    check_list = db.db_get_connections(message).keys()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btns = []
    for list_id, lst in enumerate(list_of_titles):
        if lst in check_list:
            btn = types.InlineKeyboardButton(text=f'🔗 {lst}', callback_data=f'open_list {list_id}')
        else:
            btn = types.InlineKeyboardButton(text=f'🧾 {lst}', callback_data=f'open_list {list_id}')
        btns.append(btn)
    keyboard.add(*btns)
    return keyboard


def del_inline_lists_kb(list_of_titles):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btns = []
    for list_id, lst in enumerate(list_of_titles):
        btn = types.InlineKeyboardButton(text=f'🗑 {lst}', callback_data=f'delete_list {list_id}')
        btns.append(btn)
    keyboard.add(*btns)
    return keyboard


def share_inline_lists_kb(list_of_titles):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btns = []
    for list_id, lst in enumerate(list_of_titles):
        btn = types.InlineKeyboardButton(text=f'📤 {lst}', callback_data=f'share_list {list_id}')
        btns.append(btn)
    keyboard.add(*btns)
    return keyboard


def get_inline_del_kb(dict_lop):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btns = []
    for product_id, product in dict_lop.items():
        btn = types.InlineKeyboardButton(text=f'✖ {product}', callback_data=f'delete_product {product_id}')
        btns.append(btn)
    btn1 = types.InlineKeyboardButton(text='⬅', callback_data='back')
    keyboard.add(*btns)
    keyboard.add(btn1)
    return keyboard


def get_inline_add_kb(list_of_titles):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btns = []
    for list_id, lst in enumerate(list_of_titles):
        btn = types.InlineKeyboardButton(text=f'➡ {lst}', callback_data=f'add_to_list {list_id}')
        btns.append(btn)
    keyboard.add(*btns)
    return keyboard
