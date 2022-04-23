import os

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from bot_date import DICT_URL, FIRST_NOTE, HELP_TEXT

load_dotenv()

token = os.getenv('TOKEN')


class Requester():
    def get_list(self, chat):
        b_token = self.token(chat)
        response = requests.get(DICT_URL['note_list'], headers={
            "Authorization": f"Bearer {b_token}"
        })
        return response

    def get_note(self, chat, note_id):
        url = DICT_URL['note_create']
        url_note = f'{url}{note_id}'
        b_token = self.token(chat)
        response = requests.get(url_note, headers={
            "Authorization": f"Bearer {b_token}"
        })
        return response

    def delete_note(self, chat, note_id):
        b_token = self.token(chat)
        url = DICT_URL['note_create']
        url_note = f'{url}{note_id}'
        requests.delete(url_note, headers={
            "Authorization": f"Bearer {b_token}"
        })

    def create_note(self, chat, mes_text):
        b_token = self.token(chat)
        response = requests.post(DICT_URL['note_create'], headers={
            "Authorization": f"Bearer {b_token}"
        }, data={
            "text": f"{mes_text}",
        })
        return response

    def token(self, chat):
        with open("token.txt", 'r+') as file:
            d = {}
            lines = file.readlines()
            for line in lines:
                key, value = line.split()
                d[key] = value
            b_token = d[str(chat.id)]
        return b_token


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


def note_processor(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    mes_text = update.message.text
    mes_text_spl = mes_text.split()
    if mes_text_spl[0] == 'delete' and len(mes_text_spl) == 2:
        note_del(update, context, mes_text_spl[1])
    elif mes_text.isdigit():
        note_id = int(update.message.text)
        note_detail(update, context, note_id)
    else:
        note_create(update, context, chat, mes_text, name)


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


def main():
    updater = Updater(token=token)

    updater.dispatcher.add_handler(CommandHandler('start',
                                                  api_registration))
    updater.dispatcher.add_handler(CommandHandler('help',
                                                  help))
    updater.dispatcher.add_handler(CommandHandler('refresh_token',
                                                  refresh_token))
    updater.dispatcher.add_handler(CommandHandler('note_list',
                                                  note_list_detail))
    updater.dispatcher.add_handler(MessageHandler(Filters.text,
                                                  note_processor))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
