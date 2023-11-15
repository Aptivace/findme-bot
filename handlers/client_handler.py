from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils import states, database
from config import developers, TOKEN, channel
from keyboards import client_kb

formClient = states.Client

base = database.DataBase()

client = Bot(TOKEN, parse_mode='HTML') 

chat_members = ['LEFT', 'KICKED', 'RESTRICTED'] # массив статусов для проверки пользователя

router = Router()

@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
    check_member = await client.get_chat_member(chat_id=channel, user_id=message.from_user.id) # получаем статус пользователя в канале

    if str(check_member.status).split('.')[-1] in chat_members: # проверка статуса пользователя 
        return await message.answer('Вы не подписаны на канал❗\n\nДля того чтобы оставить объявление, необходимо быть подписанным на <a href="https://t.me/NaidiMeniaMckKtits">канал</a>.')
    
    await state.set_state(formClient.ptype) # установка машины состояний
    await message.answer('<b>👋 Здравствуйте!</b>\n\n<b>В данном боте вы можете предложить <i>свое объявление</i>, но оно будет опубликовано только при соблюдении <u>ряда правил</u>:</b>\n\n1️⃣ <b> Пост может содержать только <u>ОДНУ</u> фотографию или видео <u>НЕ БОЛЬШЕ 20 СЕКУНД</u></b>\n(не добавляйте больше одного фото или видео)\n\n<b>✅ Выберите тип объявления</b>', reply_markup=client_kb.choose_type())


@router.callback_query(client_kb.Postination.filter()) # лютая функция обработки колбэка клавиатуры
async def choose_post(query: CallbackQuery, callback_data: client_kb.Postination, state: FSMContext):
    if callback_data.action == 'naydi': # нажата кнопка "Найди меня"
        await state.update_data(post_type = 'найди_меня') # запись типа поста в машину состояний
        await query.message.delete_reply_markup() # удаление клавиатуры в целях защиты от повторного нажатия 
        await query.message.edit_text('<b>📎 Прикрепите фото или видео и текст объявления\n( одним сообщением, длительность видео <i>НЕ БОЛЬШЕ</i> 20 секунд )\n\n⚠️ Если вы хотите выбрать другую опцию отправки,\nнапишите /start для перезапуска бота</b>') # редактируем сообщение бота, чтобы не засорять переписку
        await query.answer() # завершаем колбэк пустым ответом
        return await state.set_state(formClient.array) # меняем состояние на следующее 
    
    if callback_data.action == 'poteryashka': # нажата кнопка "Потеряшки"
        await state.update_data(post_type = 'потеряшка')
        await query.message.delete_reply_markup()
        await query.message.edit_text('<b>📎 Прикрепите фото или видео и текст объявления\n( одним сообщением, длительность видео <i>НЕ БОЛЬШЕ</i> 20 секунд )\n\n⚠️ Если вы хотите выбрать другую опцию отправки,\nнапишите /start для перезапуска бота</b>')
        await query.answer()
        return await state.set_state(formClient.array)

        
@router.message(formClient.array) # функция машины состояний
async def form_name(message: Message, state: FSMContext):
    if message.photo: # проверка сообщения на наличие фото
        if message.caption == None: # проверка сообщения на наличие текста (описания поста)
            await message.answer('<b>Объявление должно содержать описание❗</b>\n\n⚠️ Введите /start чтобы выложить объявление <i>заново</i>.')
            return await state.clear()
        
        await state.update_data(
            userid = message.from_user.id, # получение user_id
            media = message.photo[-1].file_id, # получение file_id последнего фото в списке (изображение высшего качества)
            description = message.caption, # получаем описание поста
            video = False # данный параметр записывается для дальнейших проверок
        )

        await message.answer('Выберите опцию отправки:', reply_markup=client_kb.anonim()) # отправка сообщения с клавиатурой
        return await state.set_state(formClient.anon) # изменение состояние на следующее
    
    if message.video: # проверка сообщения на наличие видео
        if message.caption == None:
            await message.answer('<b>Объявление должно содержать описание❗</b>\n\n⚠️ Введите /start чтобы выложить объявление <i>заново</i>.')
            return await state.clear()
        
        if message.video.duration > 21: # проверка длительности видео
            return await message.answer('<b>Длительность видео превышает <i>20</i> секунд</b>❗\n\n<b>Отправьте видео <i>короче</i> и <u>ПОВТОРНО</u> <i>укажите описание</i>.</b>')
        
        await state.update_data(
            userid = message.from_user.id,
            media = message.video.file_id,
            description = message.caption,
            video = True
        )
    
        await message.answer('Выберите опцию отправки:', reply_markup=client_kb.anonim())
        return await state.set_state(formClient.anon)

    await state.update_data(
        userid = message.from_user.id,
        media = None,
        description = message.text,
    ) # эта запись происходит, если пользователь не прикрепил медиа-файлы

    await message.answer('Выберите опцию отправки:', reply_markup=client_kb.anonim())
    await state.set_state(formClient.anon)


@router.callback_query(client_kb.Anonimation.filter())
async def choose_anon(query: CallbackQuery, callback_data: client_kb.Anonimation, state: FSMContext):
    data = await state.get_data() # получаем словарь с данными из машины состояний
    current_state = await state.get_state() # получаем актуальное состояние машины состояний (тавтология наше всё)
    if callback_data.action == 'otkat': # нажата кнопка отмены
        if current_state: # проверка на состояние
            await state.clear() # очистка и завершение машины состояний
            await query.message.delete_reply_markup()
            return await query.message.answer('⚠️ Отправка объявления отменена')
        return

    if callback_data.action == 'anon': # нажата кнопка анонимной отправки
        if data['media'] == None: # проверка на медиа-файл
            await base.create_anon(data=data) # записываем пост в БД
            await query.message.delete_reply_markup()
            await query.message.edit_text('<b>✅ Спасибо!</b>\n\nЕсли вы <b><u>корректно</u></b> предложили объявление, то, после модерации ваше объявление будет опубликовано.\nМодерация занимает до <b><i>12 часов</i></b>.\n\n<b>Список самых распространенных ошибок:</b>\n\n1️⃣ Вы предлагаете коммерческий пост\n2️⃣ Ваш пост не соответствует тематике канала\n3️⃣ Ваш пост неадекватный или содержит негативный подтекст\n\nТеперь вы знаете о всевозможных ошибках. Исправьте ошибки и предложите пост еще раз👍\n\n<b>Чтобы выложить еще одно объявления, нажмите /start</b>')
            await query.answer()
            for developer in developers: # отправка оповещения модераторам
                await client.send_message(chat_id=developer, text='<b>🛎️ Новое объявление!</b>\n\n<b>Введите <i>/pending</i> чтобы посмотреть весь список обрабатывающихся объявлений.</b>')
            return await state.clear()
        
        await base.create_anon_media(data=data)
        await query.message.delete_reply_markup()
        await query.message.edit_text('<b>✅ Спасибо!</b>\n\nЕсли вы <b><u>корректно</u></b> предложили объявление, то, после модерации ваше объявление будет опубликовано.\nМодерация занимает до <b><i>12 часов</i></b>.\n\n<b>Список самых распространенных ошибок:</b>\n\n1️⃣ Вы предлагаете коммерческий пост\n2️⃣ Ваш пост не соответствует тематике канала\n3️⃣ Ваш пост неадекватный или содержит негативный подтекст\n\nТеперь вы знаете о всевозможных ошибках. Исправьте ошибки и предложите пост еще раз👍\n\n<b>Чтобы выложить еще одно объявления, нажмите /start</b>')
        await query.answer()
        for developer in developers:
            await client.send_message(chat_id=developer, text='<b>🛎️ Новое объявление!</b>\n\n<b>Введите <i>/pending</i> чтобы посмотреть весь список обрабатывающихся объявлений.</b>')
        return await state.clear()
    
    if not query.from_user.username:
        await query.message.delete_reply_markup()
        await query.message.edit_text('<b>⛔ При отправке объявления произошла ошибка!</b>\n\nНельзя опубликовать объявление <b><u>публично</u></b> без юзернейма!\nУстановить его можно <b><i>настройках профиля</i></b>')
        await query.answer()
        return await state.clear()

    if data['media'] == None:
        await base.create_ticket(data=data, query=query)
        await query.message.delete_reply_markup()
        await query.message.edit_text('<b>✅ Спасибо!</b>\n\nЕсли вы <b><u>корректно</u></b> предложили объявление, то, после модерации ваше объявление будет опубликовано.\nМодерация занимает до <b><i>12 часов</i></b>.\n\n<b>Список самых распространенных ошибок:</b>\n\n1️⃣ Вы предлагаете коммерческий пост\n2️⃣ Ваш пост не соответствует тематике канала\n3️⃣ Ваш пост не адекватный\n\nТеперь вы знаете о всевозможных ошибках. Исправьте ошибки и предложите пост еще раз👍\n\n<b>Чтобы выложить еще одно объявления, нажмите /start</b>')
        await query.answer()
        for developer in developers:
            await client.send_message(chat_id=developer, text='<b>🛎️ Новое объявление!</b>\n\n<b>Введите <i>/pending</i> чтобы посмотреть весь список обрабатывающихся объявлений.</b>')
        return await state.clear()
    
    await base.create_ticket_media(data=data, query=query)
    await query.message.delete_reply_markup()
    await query.message.edit_text('<b>✅ Спасибо!</b>\n\nЕсли вы <b><u>корректно</u></b> предложили объявление, то, после модерации ваше объявление будет опубликовано.\nМодерация занимает до <b><i>12 часов</i></b>.\n\n<b>Список самых распространенных ошибок:</b>\n\n1️⃣ Вы предлагаете коммерческий пост\n2️⃣ Ваш пост не соответствует тематике канала\n3️⃣ Ваш пост не адекватный\n\nТеперь вы знаете о всевозможных ошибках. Исправьте ошибки и предложите пост еще раз👍\n\n<b>Чтобы выложить еще одно объявления, нажмите /start</b>')
    await query.answer()
    await state.clear()
    for developer in developers:
        await client.send_message(chat_id=developer, text='<b>🛎️ Новое объявление!</b>\n\n<b>Введите <i>/pending</i> чтобы посмотреть весь список обрабатывающихся объявлений.</b>')
    

        


