import time

import telebot
from requests.exceptions import ReadTimeout, ConnectionError

from business import *

ADMIN_ID_LIST = ['616356243', '1760269999']
IS_DEBUG = True
AUTHENTICATION_TOKEN = '6392565799:AAFzQy4uesuvZ-5gOhCcrvhYr_xdSalYqI8' if IS_DEBUG else '6037063888:AAHVm-IjLif82Wt' \
                                                                                         '-CNykhrRU3VsJqtecjYI'
CHAT_URL = 'https://t.me/+vQm5jYWTWo1iZmMy'
bot = telebot.TeleBot(AUTHENTICATION_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    print_log(f'{message.chat.id} run bot')
    bot.send_message(message.chat.id, f'Привіт. Ми раді, що ти завітав до нас 🙂\nНаш чат: {CHAT_URL}')
    home(message, bot)


@bot.message_handler(func=lambda message: True)
def handle_exchange_button_click(message):
    if str(message.chat.id) in ADMIN_ID_LIST:
        if 'Пеєр для обміну:' in message.text and len(message.text) > 16:
            set_payeer_account(message.text.split(':')[1].replace(' ', ''))
            bot.send_message(message.chat.id, 'Виконано')
        elif 'Курс з пеєра долар на карту гривню:' in message.text and len(message.text) > 34:
            set_payeer_usd_to_uah_course(message.text.split(':')[1].replace(' ', ''))
            bot.send_message(message.chat.id, 'Виконано')

    if message.text == 'Головна':
        home(message, bot)
    elif message.text == 'Payeer USD\n' + 'Карта UAH':
        exchange_payeer_usd_to_uah(message, bot)
    elif message.text == 'Курс обміну':
        course(message, bot)
    elif message.text == 'Підтримка':
        support(message, bot)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    photo = message.photo[-1]
    photo_id = photo.file_id
    chat_id = -993312734 if IS_DEBUG else -1001749858927
    markup = types.ReplyKeyboardMarkup(row_width=1)
    home_button = types.KeyboardButton('Головна')

    markup.add(
        home_button,
    )
    if message.caption:
        bot.send_photo(chat_id, photo_id, caption=f'id: {message.chat.id}\n{message.caption}')
        bot.send_message(message.chat.id, f'Заявку прийнято. Обмін відбудеться протягом 48 годин❗️',
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Виконуйте інструкцію❗️')


def main():
    bot.polling()


if __name__ == '__main__':
    while True:
        try:
            main()
        except (ReadTimeout, ConnectionError):
            print_log("Error with Internet connection")
            time.sleep(1)
            continue
