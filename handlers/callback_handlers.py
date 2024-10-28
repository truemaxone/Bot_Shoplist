import keyboards
from aiogram import types
from bot import db
from dispatcher import bot, dp
from fsm import AdditionalStep


@dp.callback_query_handler(lambda callback_query: True)
async def callback_inline(call: types.CallbackQuery):
    dict_of_lists = db.db_recourse(call)
    list_of_titles = list(dict_of_lists.keys())
    owned_titles = db.db_get_owned_titles(call)

    if call.message and dict_of_lists and list_of_titles:
        if call.data == 'delete':
            temp = call.message.text.split(':')[0]
            title = temp[temp.index('"') + 1: temp.rindex('"')]
            current_dict = dict_of_lists[title]
            keyboard = keyboards.get_inline_del_kb(current_dict)
            await bot.edit_message_text('Что удалить из списка?', call.message.chat.id,
                                        call.message.message_id, reply_markup=keyboard)

        elif call.data == 'back':
            keyboard = keyboards.get_inline_lists_kb(list_of_titles, call)
            await bot.edit_message_text('Ниже перечень всех твоих списков:\nДля просмотра нажми на нужный.',
                                        call.message.chat.id, call.message.message_id, reply_markup=keyboard)

        elif 'delete_list ' in call.data:
            list_id = int(call.data.replace('delete_list ', ''))
            keyboard = keyboards.get_del_list_kb()
            await bot.edit_message_text(f'⚠ Ты точно хочешь удалить список "{list_of_titles[list_id]}"?'
                                        f'\nЯ удалю его безвозвратно.',
                                        call.message.chat.id, call.message.message_id, reply_markup=keyboard)

        elif call.data == 'delete_list_yes':
            title = call.message.text[call.message.text.index('"') + 1: call.message.text.rindex('"')]
            await bot.edit_message_text(chat_id=call.message.chat.id, text=f'✅ Список "{title}" удален.',
                                        message_id=call.message.message_id,
                                        reply_markup=None)
            del dict_of_lists[title]
            db.db_update(call, dict_of_lists)
            connections = db.db_get_connections(call)
            connected = connections.keys()
            if title in connected:
                db.db_del_connection(call, title)
            owned_titles.remove(title)
            db.db_update_owned_titles(call, owned_titles)
        elif call.data == 'delete_list_no':
            await bot.edit_message_text(chat_id=call.message.chat.id, text='Нет так нет...',
                                        message_id=call.message.message_id,
                                        reply_markup=None)

        elif 'open_list' in call.data:
            list_id = int(call.data.replace('open_list ', ''))
            db.db_update_current_list_id(call, list_id)
            dict_lop = dict_of_lists[list_of_titles[list_id]]
            list_of_msgs = split_message(dict_lop)
            if dict_lop:
                keyboard = keyboards.get_show_kb()
                if len(list_of_msgs) < 2:
                    await bot.edit_message_text((f'Ниже список товаров из списка "{list_of_titles[list_id]}":\n\n' +
                                                 line_print(dict_lop)), call.message.chat.id, call.message.message_id,
                                                reply_markup=keyboard)
                else:
                    await bot.edit_message_text((f'Ниже список товаров из списка "{list_of_titles[list_id]}":\n\n' +
                                                 ''.join(list_of_msgs[0])), call.message.chat.id, call.message.message_id,
                                                reply_markup=keyboard)
                    for msg in list_of_msgs[1:]:
                        await bot.send_message(call.message.chat.id, (f'Продолжение списка товаров из списка '
                                                                      f'"{list_of_titles[list_id]}":\n\n' +
                                                                      ''.join(msg)), reply_markup=keyboard)

            else:
                await call.message.answer("ℹ Список пуст.")

        elif 'add_to_list' in call.data:
            list_id = int(call.data.replace('add_to_list ', ''))
            db.db_update_current_list_id(call, list_id)
            title_to_update = list_of_titles[list_id]
            connections = db.db_get_connections(call)
            connected_lists = connections.keys()
            if title_to_update in connected_lists:
                await AdditionalStep.add_next_connected_message.set()
                await bot.edit_message_text(chat_id=call.message.chat.id,
                                            text=f'Был выбран список "{title_to_update}".\n'
                                                 f'Это *общий* список на {len(connections)} человек, включая '
                                                 f'тебя.\nТеперь напиши названия продуктов через запятую или enter, '
                                                 f'или через запятую и интер, пиши как тебе проще, я все пойму.',
                                            message_id=call.message.message_id, parse_mode='Markdown',
                                            reply_markup=None)
            else:
                await AdditionalStep.add_next_message.set()
                await bot.edit_message_text(chat_id=call.message.chat.id,
                                            text=f'Был выбран список "{title_to_update}".\n'
                                                 f'Это твой *личный* список.\n'
                                                 f'Теперь напиши названия продуктов через запятую или enter, или через '
                                                 f'запятую и интер, пиши как тебе проще, я все пойму.',
                                            message_id=call.message.message_id, parse_mode='Markdown',
                                            reply_markup=None)

        elif 'share_list' in call.data:
            list_id = int(call.data.replace('share_list ', ''))
            db.db_update_current_list_id(call, list_id)
            await AdditionalStep.share_list_next_message.set()
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        text=f'Был выбран список "{list_of_titles[list_id]}".'
                                             f'\nТеперь напиши ID того с кем хочем поделиться списком.'
                                             f'\nID можно узнать с помощью команды /get_my_id.'
                                             f'\n⚠ Списком можно поделиться только с моими подписчиками.',
                                        message_id=call.message.message_id, reply_markup=None)

        elif 'delete_product' in call.data:
            product_id = call.data.replace('delete_product ', '')
            current_list_id = db.db_get_current_list_id(call)
            current_title = list_of_titles[current_list_id]
            dict_lop = dict_of_lists[current_title]
            connections = db.db_get_connections(call)
            connected_lists = connections.keys()
            if dict_lop:
                temp = dict_lop.pop(product_id)
                dict_of_lists[current_title] = dict_lop
                if current_title in connected_lists:
                    db.db_update_connected(call, dict_lop, current_title)
                    users = connections[current_title]
                    for user in users:
                        await bot.send_message(user, f'⚠ Пользователь {db.db_get_name_by_id(call.from_user.id)} удалил '
                                                     f'*{temp}* из общего списка "{current_title}".',
                                                     parse_mode='Markdown')
                else:
                    db.db_update(call, dict_of_lists)
                await call.message.answer(f'✅ Удалил *{temp}* из списка.', parse_mode='Markdown')
            else:
                await call.message.answer("ℹ Список пуст.")

            keyboard = keyboards.get_inline_del_kb(dict_lop)
            await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                                reply_markup=keyboard)
    else:
        await bot.edit_message_text('ℹ Список пуст.', call.message.chat.id, call.message.message_id)


#  Вывод пронумированных продуктов в столбик
def line_print(dict_lop):
    new_line = ''
    for i, item in enumerate(dict_lop.values()):
        new_line += (str(int(i) + 1) + ') ' + item + '\n')
    return new_line


# Разбивка длинных сообщений
def split_message(dict_lop):
    messages = []
    for i, item in enumerate(dict_lop.values()):
        message_part = (str(int(i) + 1) + ') ' + item + '\n')
        if messages:
            if (len(''.join(messages[-1])) + len(message_part)) < 4000:
                messages[-1].append(message_part)
            else:
                messages.append([message_part])
        else:
            messages.append([message_part])
    return messages
