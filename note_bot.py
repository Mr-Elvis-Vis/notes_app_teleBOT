import os

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from bot_date import DICT_URL, FIRST_NOTE

load_dotenv()

token = os.getenv('TOKEN')


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
        note_create(update, context)
        note_list_detail(update, context)
    else:
        context.bot.send_message(chat.id, 'Упс! Что-то не так!')


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


def note_list_detail(update, context):
    chat = update.effective_chat
    with open("token.txt", 'r+') as file:
        d = {}
        lines = file.readlines()
        for line in lines:
            key, value = line.split()
            d[key] = value
        b_token = d[str(chat.id)]
        response = requests.get(DICT_URL['note_list'], headers={
            "Authorization": f"Bearer {b_token}"
        })
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


def note_create(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    mes_text = update.message.text
    mes_text_spl = mes_text.split()
    if mes_text == '/start':
        mess = FIRST_NOTE
        with open("token.txt", 'r+') as file:
            d = {}
            lines = file.readlines()
            for line in lines:
                key, value = line.split()
                d[key] = value
            b_token = d[str(chat.id)]
            response = requests.post(DICT_URL['note_create'], headers={
                "Authorization": f"Bearer {b_token}"
            }, data={
                "text": f"{mess}",
            })
    elif mes_text_spl[0] == 'DEL' and len(mes_text_spl) == 2:
        note_del(update, context, mes_text_spl[1])
    else:
        try:
            note_id = int(update.message.text)
            note_detail(update, context, note_id)
        except:
            mess = update.message.text
            with open("token.txt", 'r+') as file:
                d = {}
                lines = file.readlines()
                for line in lines:
                    key, value = line.split()
                    d[key] = value
                b_token = d[str(chat.id)]
                response = requests.post(DICT_URL['note_create'], headers={
                    "Authorization": f"Bearer {b_token}"
                }, data={
                    "text": f"{mess}",
                })

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
                try:
                    note_list_detail(update, context)
                except RuntimeError:
                    pass


def note_detail(update, context, note_id):
    chat = update.effective_chat
    with open("token.txt", 'r+') as file:
        d = {}
        lines = file.readlines()
        for line in lines:
            key, value = line.split()
            d[key] = value
        b_token = d[str(chat.id)]
        url = DICT_URL['note_create']
        url_note = f'{url}{note_id}'
        response = requests.get(url_note, headers={
            "Authorization": f"Bearer {b_token}"
        })
        response = response.json()
        message = response.get('text')
        name = update.message.chat.first_name
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
    try:
        note_id = int(mes_text)
        with open("token.txt", 'r+') as file:
            d = {}
            lines = file.readlines()
            for line in lines:
                key, value = line.split()
                d[key] = value
            b_token = d[str(chat.id)]
            url = DICT_URL['note_create']
            url_note = f'{url}{note_id}'
            requests.delete(url_note, headers={
                "Authorization": f"Bearer {b_token}"
            })
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
        context.bot.send_message(
            chat_id=chat.id,
            text='Введите корректный номер заметки для удаления!',
            reply_markup=button
        )


def help(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([
        ['/note_list'],
        ['/refresh_token'], ['/help']
    ],
        resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text=(
            f'Привет, {name}!\nСписок команд бота:\nstart - инициализирует '
            f'тебя как пользователя для дальнейшей работы\nhelp - ты сейчас '
            f'здесь! =)\nrefresh_token - если после работы с ботом возникли '
            f'какие-то проблемы, попробуй попросить бота обновить токен '
            f'доступа\nnote_list - выдаст список всех твоих заметок\n '
            f'~число~ введи номер заметки, чтобы посмотреть её подробно\n '
            f'DEL ~число~ для удаления заметки **вводи ID заметки!\nПросто '
            f'отправь текст этому боту и он создаст новую заметку!'
        ),
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
                                                  note_create))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
