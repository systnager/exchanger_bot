import json

import telebot
from telebot import types

from datetime import datetime

AUTHENTICATION_TOKEN = '6037063888:AAHVm-IjLif82Wt-CNykhrRU3VsJqtecjYI'
bot = telebot.TeleBot(AUTHENTICATION_TOKEN)


def get_config():
    config_file = open("config.json")
    config = json.load(config_file)
    config_file.close()
    return config


def home(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    exchange_payeer_usd_to_uah_button = types.KeyboardButton('Обмін Payeer USD -> UAH')
    course_button = types.KeyboardButton('Курс обміну')
    support_button = types.KeyboardButton('Підтримка')

    markup.add(
        exchange_payeer_usd_to_uah_button,
        course_button,
        support_button,
    )

    bot.send_message(message.chat.id, 'Оберіть дію', reply_markup=markup)


def exchange_payeer_usd_to_uah(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    current_date = datetime.now().strftime('%Y-%m-%d')
    home_button = types.KeyboardButton('Головна')

    config = get_config()
    markup.add(
        home_button,
    )
    bot.send_message(message.chat.id, f'Відправте суму для обміну на {config["payeer_account"]} від 0.2$ з коментарем ' +
                     f'"Ваша_карта {current_date}". Обмін відбудеться протягом 48 годин', reply_markup=markup)


def course(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    current_date = datetime.now().strftime('%Y-%m-%d')
    home_button = types.KeyboardButton('Головна')

    config = get_config()

    markup.add(
        home_button,
    )
    bot.send_message(message.chat.id, f'Курс на {current_date}\n' +
                     f'1 Payeer USD -> {config["payeer_usd_to_uah"]} UAH', reply_markup=markup)


def support(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    home_button = types.KeyboardButton('Головна')

    markup.add(
        home_button,
    )
    bot.send_message(message.chat.id, f'Для підтримки напишіть @arobotok202118 або @systnager', reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    home(message)


@bot.message_handler(func=lambda message: True)
def handle_exchange_button_click(message):
    if message.text == 'Головна':
        home(message)
    elif message.text == 'Обмін Payeer USD -> UAH':
        exchange_payeer_usd_to_uah(message)
    elif message.text == 'Курс обміну':
        course(message)
    elif message.text == 'Підтримка':
        support(message)


def main():
    bot.polling()


if __name__ == '__main__':
    main()
