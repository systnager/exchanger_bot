from datetime import datetime
from telebot import types
import json


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


def home(message, bot):
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


def exchange_payeer_usd_to_uah(message, bot):
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


def course(message, bot):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    current_date = datetime.now().strftime('%Y.%m.%d')
    home_button = types.KeyboardButton('Головна')

    config = get_config()

    markup.add(
        home_button,
    )
    bot.send_message(message.chat.id, f'Курс на {current_date}\n' +
                     f'1 Payeer USD ➡️ {config["payeer_usd_to_uah"]} UAH', reply_markup=markup)


def support(message, bot):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    home_button = types.KeyboardButton('Головна')

    markup.add(
        home_button,
    )
    bot.send_message(message.chat.id,
                     f'Контакти для отриманя підтримки: @arobotok202118 та @systnager', reply_markup=markup)
