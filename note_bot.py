import os

from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from registration_and_token import api_registration, refresh_token
from actions import note_detail, note_list_detail, note_create, note_del, help

load_dotenv()

token = os.getenv('TOKEN')


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
