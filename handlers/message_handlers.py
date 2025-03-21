import keyboards
from handlers import states
from fsm import AdditionalStep
from aiogram import types
from dispatcher import bot, dp
from bot import db


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    sti = open('static/welcome.webp', 'rb')
    await message.answer_sticker(sti)
    keyboard = keyboards.get_main_kb()
    bot_name = await bot.get_me()

    await message.answer(f"Добро пожаловать, {message.from_user.first_name}!\nЯ - *{bot_name.first_name}* 🤖, "
                         f"бот созданный чтобы помогать со списком покупок.\nДля подробной информации по командам, "
                         f"введите /help", parse_mode='Markdown', reply_markup=keyboard)

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    db.db_add_user(user_id, user_name)


@dp.message_handler(commands=['stop'])
async def goodbye(message: types.Message):
    if db.db_check_existence(message):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        await message.answer(f"Было приятно помогать тебе {user_name}."
                             f"\nСпасибо за доверие. Если тебе когда-нибудь снова понадобиться моя помощь, ты знаешь, "
                             f"где меня найти..."
                             f"\nВсего доброго.👋🏼")

        db.db_delete_user(user_id)
    else:
        await message.answer("🫧 Извини, но ты еще не зарегистрировался. Чтобы начать работу со мной введи /start")


@dp.message_handler(commands=['show_buttons'])
async def get_buttons(message: types.Message):
    if db.db_check_existence(message):
        keyboard = keyboards.get_main_kb()
        await message.answer('Лови клавиатуру ⌨', reply_markup=keyboard)
    else:
        await message.answer("🫧 Извини, но ты еще не зарегистрировался. Чтобы начать работу со мной введи /start")


@dp.message_handler(commands=['get_my_id'])
async def get_id(message: types.Message):
    user_id = message.from_user.id
    await message.answer(f"Твой ID чтобы делиться списками - *{user_id}*.", parse_mode='Markdown')


@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):
    await message.answer("Ниже небольшое INFO по командам:"
                         "\n\n⌨ /show_buttons - показать кнопки для общения со мной, если пропали."
                         "\n🆘 /help - справочная информация"
                         "\n🆔 /get_my_id - выведет твой id"
                         "\n⛔ /stop - отписаться от бота"
                         "\n🫶🏼Также было бы приятно получить от тебя feedback."
                         "\n💡Если не сложно, напиши, что по твоему мнению нужно добавить/убрать/переделать."
                         "\n💬Пиши напрямую ему @truemahoney, он все сделает.🗿")


@dp.message_handler(commands=['add_list'])
async def add_list(message: types.Message):
    if db.db_check_existence(message):
        await message.answer("Как назовем новый список?")
        await AdditionalStep.add_list_next_message.set()
    else:
        await message.answer("🫧 Извини, но ты еще не зарегистрировался. Чтобы начать работу со мной введи /start")


@dp.message_handler(commands=['add_product', 'show_lists', 'delete_list', 'share_list'])
async def manage_lists(message: types.Message):
    command = message.text
    if db.db_check_existence(message):
        dict_of_lists = db.db_recourse(message)
        list_of_titles = list(dict_of_lists.keys())
        if list_of_titles:
            if command == 'Добавить продукты':
                keyboard = keyboards.manage_inline_lists_kb(list_of_titles, 'add_to_list')
                await message.answer('В какой список занести продукты?', reply_markup=keyboard)
            elif command == 'Показать списки':
                keyboard = keyboards.get_inline_lists_kb(list_of_titles, message)
                await message.answer('Ниже перечень всех твоих списков.\nДля просмотра нажми на нужный.',
                                     reply_markup=keyboard)
            elif command == 'Удалить список':
                keyboard = keyboards.manage_inline_lists_kb(list_of_titles, 'delete_list')
                await message.answer('Выбери список, который мне нужно удалить:', reply_markup=keyboard)
            elif command == 'Поделиться списком':
                keyboard = keyboards.manage_inline_lists_kb(list_of_titles, 'share_list')
                await message.answer('Выбери список, которым хочешь поделиться:', reply_markup=keyboard)
        else:
            await message.answer("🫧 Извини, но у тебя еще нет ни одного списка. Сначала необходимо создать хотя бы "
                                 "один.")
    else:
        await message.answer("🫧 Извини, но ты еще не зарегистрировался. Чтобы начать работу со мной введи /start")


@dp.message_handler(content_types=['text'])
async def bot_answer(message: types.Message):
    if message.chat.type == 'private':
        if message.text == 'Показать списки':
            await manage_lists(message)
        elif message.text == 'Добавить список':
            await add_list(message)
        elif message.text == 'Добавить продукты':
            await manage_lists(message)
        elif message.text == 'Удалить список':
            await manage_lists(message)
        elif message.text == 'Поделиться списком':
            await manage_lists(message)
        else:
            await message.answer('Извини, я не знаю такой команды 🗿'
                                 '\nДля общения со мной можешь использовать кнопки или напиши /help, там небольшое '
                                 'INFO по командам.')
