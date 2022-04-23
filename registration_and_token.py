import requests
from telegram import ReplyKeyboardMarkup

from actions import note_create, note_list_detail
from bot_date import DICT_URL, FIRST_NOTE


def api_registration(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([
        ['/note_list'],
        ['/refresh_token'], ['/help']
    ],
        resize_keyboard=True)
    response_user = requests.post(DICT_URL['auth'], data={
        "username": f"{chat.id}",
        "password": f"{name}PaSsWrD"
    })
    with open('pass.txt', 'a') as file:
        file.writelines(f'{chat.id} {name}PaSsWrD\n')
    if response_user.status_code == 201:
        refresh_token(update, context)
        context.bot.send_message(
            chat_id=chat.id,
            text='Пользователь успешно создан!',
            reply_markup=button
        )
        note_create(update, context, chat, FIRST_NOTE, name)
        note_list_detail(update, context)
    else:
        context.bot.send_message(chat.id, 'Упс! Что-то не так! Может вы уже '
                                          'имеете список заметок?')


def refresh_token(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    response_token = requests.post(DICT_URL['token'], data={
        "username": f"{chat.id}",
        "password": f"{name}PaSsWrD"
    })
    response = response_token.json()
    b_token = response.get('access')
    with open('token.txt', 'a') as file:
        file.writelines(f'{chat.id} {b_token}\n')
    button = ReplyKeyboardMarkup([
        ['/note_list'],
        ['/refresh_token'], ['/help']
    ],
        resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Токен успешно обновлён',
        reply_markup=button
    )
