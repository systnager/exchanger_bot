from requests.exceptions import ReadTimeout, ConnectionError
import json
import time

import telebot
from telebot import types

from datetime import datetime

ADMIN_ID_LIST = ['616356243', '1760269999']
IS_DEBUG = True
AUTHENTICATION_TOKEN = '6392565799:AAFzQy4uesuvZ-5gOhCcrvhYr_xdSalYqI8' if IS_DEBUG else '6037063888:AAHVm-IjLif82Wt' \
                                                                                         '-CNykhrRU3VsJqtecjYI'
CHAT_URL = 'https://t.me/+vQm5jYWTWo1iZmMy'
bot = telebot.TeleBot(AUTHENTICATION_TOKEN)


def print_log(log_text):
    print(f'{datetime.now()} {log_text}')


def save_config(config):
    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=4)


def get_config():
    with open("config.json", "r") as config_file:
        return json.load(config_file)


def set_payeer_usd_to_uah_course(_course):
    config = get_config()
    config["payeer_usd_to_uah"] = _course
    save_config(config)


def set_payeer_account(payeer_account):
    config = get_config()
    config["payeer_account"] = payeer_account
    save_config(config)


def home(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    exchange_payeer_usd_to_uah_button = types.KeyboardButton('Payeer USD\n' + 'Карта UAH')
    course_button = types.KeyboardButton('Курс обміну')
    support_button = types.KeyboardButton('Підтримка')

    markup.add(
        exchange_payeer_usd_to_uah_button,
        course_button,
        support_button,
    )

    bot.send_message(message.chat.id, 'Ви на головній!', reply_markup=markup)


def exchange_payeer_usd_to_uah(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    home_button = types.KeyboardButton('Головна')

    config = get_config()
    markup.add(
        home_button,
    )

    bot.send_message(message.chat.id,
                     f'❗️❗️❗️УВАГА❗️❗️❗️\nУ разі невиконання інструкцій адміністрація має право не проводити Вам обмін')
    bot.send_message(message.chat.id,
                     f'Відправте суму для обміну на {config["payeer_account"]} від 0.2$ з коментарем: ' +
                     f'Ваша_карта Ваш_нік')
    bot.send_message(message.chat.id, f'Надішліть скрін переказу в бот з коментарем під ним. ' +
                     f'Лише після цього заявку буде прийнято на розгляд',
                     reply_markup=markup)


def course(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    current_date = datetime.now().strftime('%Y.%m.%d')
    home_button = types.KeyboardButton('Головна')

    config = get_config()

    markup.add(
        home_button,
    )
    bot.send_message(message.chat.id, f'Курс на {current_date}\n' +
                     f'1 Payeer USD ➡️ {config["payeer_usd_to_uah"]} UAH', reply_markup=markup)


def support(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    home_button = types.KeyboardButton('Головна')

    markup.add(
        home_button,
    )
    bot.send_message(message.chat.id,
                     f'Контакти для отриманя підтримки: @arobotok202118 та @systnager', reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    print_log(f'{message.chat.id} run bot')
    bot.send_message(message.chat.id, f'Привіт. Ми раді, що ти завітав до нас 🙂\nНаш чат: {CHAT_URL}')
    home(message)


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
        home(message)
    elif message.text == 'Payeer USD\n' + 'Карта UAH':
        exchange_payeer_usd_to_uah(message)
    elif message.text == 'Курс обміну':
        course(message)
    elif message.text == 'Підтримка':
        support(message)


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
