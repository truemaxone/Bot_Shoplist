import config

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


def get_show_simple_kb():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
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


def manage_inline_lists_kb(list_of_titles, callback_data):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btns = []
    for list_id, lst in enumerate(list_of_titles):
        if callback_data == 'delete_list':
            text = f'🗑 {lst}'
        elif callback_data == 'share_list':
            text = f'📤 {lst}'
        elif callback_data == 'add_to_list':
            text = f'➡ {lst}'
        else:
            continue
        btn = types.InlineKeyboardButton(text=text, callback_data=f'{callback_data} {list_id}')
        btns.append(btn)

    keyboard.add(*btns)
    return keyboard


def get_inline_del_kb(dict_lop, message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btns = []
    page_limit = len(dict_lop) // config.ITEMS_PER_PAGE + 1
    cur_page = db.db_get_current_page(message)
    if len(dict_lop) < config.ITEMS_PER_PAGE + 1:
        for product_id, product in dict_lop.items():
            btn = types.InlineKeyboardButton(text=f'✖ {product}', callback_data=f'delete_product {product_id}')
            btns.append(btn)
    else:
        splitted_dict = dict(list(dict_lop.items())[(cur_page - 1)
                                                    * config.ITEMS_PER_PAGE:config.ITEMS_PER_PAGE * cur_page])
        for product_id, product in splitted_dict.items():
            btn = types.InlineKeyboardButton(text=f'✖ {product}', callback_data=f'delete_product {product_id}')
            btns.append(btn)

    keyboard.add(*btns)

    if len(dict_lop) > 25:
        btn0 = types.InlineKeyboardButton(text='◀ предыдущая', callback_data='prev_page')
        btn1 = types.InlineKeyboardButton(text='следующая ▶', callback_data='next_page')
        if cur_page == 1:
            keyboard.add(btn1)
        elif cur_page == page_limit:
            keyboard.add(btn0)
        else:
            keyboard.add(btn0, btn1)

    btn2 = types.InlineKeyboardButton(text='⬅', callback_data='back_to_list')
    keyboard.add(btn2)
    return keyboard
