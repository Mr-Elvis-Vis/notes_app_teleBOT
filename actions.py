from telegram import ReplyKeyboardMarkup

from bot_date import HELP_TEXT
from requester import Requester


def note_list_detail(update, context):
    request = Requester()
    chat = update.effective_chat
    response = request.get_list(chat)
    response = response.json()
    message = ''
    for i in response:
        text = i.get('text')[:50]
        note_id = i.get('id')
        mes = f'ID заметки: {note_id}. Текст: {text}\n'
        message += mes
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([
        ['/note_list'],
        ['/refresh_token'], ['/help']
    ],
        resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text=f'Список твоих заметок, {name}: \n {message}',
        reply_markup=button
    )


def note_detail(update, context, note_id):
    request = Requester()
    chat = update.effective_chat
    response = request.get_note(chat, note_id)
    response = response.json()
    message = response.get('text')
    button = ReplyKeyboardMarkup([
        ['/note_list'],
        ['/refresh_token'], ['/help']
    ],
        resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text=f'Заметка {note_id}: \n {message}',
        reply_markup=button
    )


def note_del(update, context, mes_text):
    chat = update.effective_chat
    note_id = int(mes_text)
    try:
        request = Requester()
        request.delete_note(chat, note_id)
        button = ReplyKeyboardMarkup([
            ['/note_list'],
            ['/refresh_token'], ['/help']
        ],
            resize_keyboard=True)
        context.bot.send_message(
            chat_id=chat.id,
            text=f'Заметка {note_id} удалена',
            reply_markup=button
        )
        note_list_detail(update, context)
    except:
        button = ReplyKeyboardMarkup([
            ['/note_list'],
            ['/refresh_token'], ['/help']
        ],
            resize_keyboard=True)
        context.bot.send_message(
            chat_id=chat.id,
            text='Введите корректный номер заметки для удаления!',
            reply_markup=button
        )


def note_create(update, context, chat, mes_text, name):
    request = Requester()
    response = request.create_note(chat, mes_text)
    button = ReplyKeyboardMarkup([
        ['/note_list'],
        ['/refresh_token'], ['/help']
    ],
        resize_keyboard=True)
    if response.status_code == 201:
        context.bot.send_message(
            chat_id=chat.id,
            text=f'{name}! Заметка создана!',
            reply_markup=button
        )
    else:
        context.bot.send_message(
            chat.id,
            'Упс! Что-то не так!',
            reply_markup=button
        )
        note_list_detail(update, context)


def help(update, context):
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([
        ['/note_list'],
        ['/refresh_token'], ['/help']
    ],
        resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text=HELP_TEXT,
        reply_markup=button
    )
