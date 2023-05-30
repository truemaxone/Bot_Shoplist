from aiogram import types
from aiogram.dispatcher import FSMContext
from bot import db
from dispatcher import bot, dp
from fsm import AdditionalStep


@dp.message_handler(state=AdditionalStep.add_list_next_message)
async def additional_list(message: types.Message, state: FSMContext):
    dict_of_lists = db.db_recourse(message)
    list_of_titles = list(dict_of_lists.keys())
    owned_lists = db.db_get_owned_titles(message)

    async with state.proxy() as data:
        data['add_list_next_message'] = message.text
        lot_for_checking = [lst.lower() for lst in list_of_titles]
        # Проверка на случайное нажатие кнопок бота
        if message.text in ['Показать списки', 'Добавить список', 'Добавить продукты', 'Удалить список',
                            'Поделиться списком']:
            await message.answer('Похоже была нажата кнопка для общения со мной, попробуй еще раз...')

        elif message.text.strip().lower() in lot_for_checking:
            await message.answer(f'⚠ Список с названием "{message.text.strip()}" уже существует.')
        else:
            dict_of_lists[message.text.strip()] = {}
            db.db_update(message, dict_of_lists)
            await message.answer(f'✅ Добавил список "{message.text.strip()}". Хороших покупок!')
            owned_lists.append(message.text.strip())
            db.db_update_owned_titles(message, owned_lists)
    await state.finish()


@dp.message_handler(state=AdditionalStep.share_list_next_message)
async def share_list_step(message: types.Message, state: FSMContext):
    dict_of_lists = db.db_recourse(message)
    list_of_titles = list(dict_of_lists.keys())
    current_title = list_of_titles[db.db_get_current_list_id(message)]
    users = db.db_get_users()
    done_flag = True

    async with state.proxy() as data:
        data['share_list_next_message'] = message.text
        connected_data = db.db_get_connections(message)
        try:
            friend_id = int(message.text.strip())
            if friend_id not in users:
                await message.answer(f'⚠ Пользователя с ID {friend_id} нет в моей базе.'
                                     f'\nПроверь ID и попробуй еще раз.')
            else:
                if current_title not in connected_data:
                    friend_titles = db.db_get_friend_titles(friend_id)
                    if current_title in friend_titles:
                        await message.answer(f'⚠ У этого пользователя уже есть список с названием "{current_title}".')
                        done_flag = False
                    else:
                        connected_data[current_title] = [friend_id]
                        # Оповещения обоим о шеринге
                        await message.answer(f'✅ Поделился списком "{current_title}" c ID {friend_id}')
                        await bot.send_message(friend_id, f"ℹ Тебе предоставили доступ к списку {current_title}")
                else:
                    temp_list = connected_data[current_title].copy()
                    if friend_id not in temp_list:
                        temp_list.append(friend_id)
                        connected_data[current_title] = temp_list
                        # Оповещения обоим о шеринге
                        await message.answer(f'✅ Поделился списком "{current_title}" c ID {friend_id}')
                        await bot.send_message(friend_id, f"ℹ Тебе предоставили доступ к списку {current_title}")
                    else:
                        done_flag = False
                        await message.answer(f'ℹ Ты уже поделился списком "{current_title}" c ID {friend_id}')
                if done_flag:
                    db.db_add_connection(message, connected_data, current_title)
        except ValueError:
            await message.answer('⚠ ID пользователя должен состоять из цифр.')
        await state.finish()


@dp.message_handler(state=AdditionalStep.add_next_message)
async def adding_product(message: types.Message, state: FSMContext):
    dict_of_lists = db.db_recourse(message)

    async with state.proxy() as data:
        data['add_next_message'] = message.text
        # Проверка на случайное нажатие кнопок бота
        if message.text in ['Показать списки', 'Добавить список', 'Добавить продукты', 'Удалить список',
                            'Поделиться списком']:
            await message.answer('Похоже была нажата кнопка для общения со мной, попробуй еще раз...')
        else:
            products = message_proc(message)
            await product_proc(message, dict_of_lists, products)
    await state.finish()


@dp.message_handler(state=AdditionalStep.add_next_connected_message)
async def adding_product_connected(message: types.Message, state: FSMContext):
    dict_of_lists = db.db_recourse(message)

    async with state.proxy() as data:
        data['add_next_connected_message'] = message.text
        # Проверка на случайное нажатие кнопок бота
        if message.text in ['Показать списки', 'Добавить список', 'Добавить продукты', 'Удалить список',
                            'Поделиться списком']:
            await message.answer('Похоже была нажата кнопка для общения со мной, попробуй еще раз...')
        else:
            products = message_proc(message)
            await product_proc(message, dict_of_lists, products, connected=True)
    await state.finish()


async def product_proc(message, dict_of_lists, products, connected=False):
    list_of_titles = list(dict_of_lists.keys())
    current_list_id = db.db_get_current_list_id(message)
    current_title = list_of_titles[current_list_id]
    current_dict = dict_of_lists[current_title]
    lop_for_checking = [product.lower() for product in current_dict.values()]
    products = [product.strip() for product in products]
    bag = []  # для вывода нескольких добавленных в список продуктов в сообщении
    for product in products:
        if product.lower() in lop_for_checking:
            await message.answer(f"ℹ {product} уже есть в списке.")
        else:
            if current_dict.keys():
                new_id = str(int(list(current_dict.keys())[-1]) + 1)
            else:
                new_id = '0'
            current_dict[new_id] = product
            bag.append(product.strip())
    dict_of_lists[current_title] = current_dict
    if not connected:
        db.db_update(message, dict_of_lists)
    else:
        db.db_update_connected(message, current_dict, current_title)
        users = db.db_get_connections(message)[current_title]
        for user in users:
            if bag:
                if len(bag) == 1:
                    await bot.send_message(user, f'✅ Занес {bag[0]} в общий список "{current_title}".')
                else:
                    await bot.send_message(user, f'✅ {", ".join(bag)}  - все занес в общий список "{current_title}".')
    if bag:
        if len(bag) == 1:
            await message.answer(f"✅ Занес {bag[0]} в список.")
        else:
            await message.answer(f"✅ {', '.join(bag)}  - все занес в список.")


# Обработка сообщения со списком продуктов
def message_proc(message):
    if '\n' in message.text:
        products = message.text.replace(', ', '\n').replace(',', '\n').split('\n')
    elif ',' in message.text:
        products = message.text.replace(', ', ',').split(',')
    else:
        products = [message.text.strip()]
    return products
