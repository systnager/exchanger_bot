import time

import telebot as _telebot
from telebot import types
from requests.exceptions import ReadTimeout, ConnectionError

from business import *

ADMIN_ID_LIST = [
    '616356243',
    '1760269999'
]
IS_DEBUG = True
AUTHENTICATION_TOKEN = '6392565799:AAFzQy4uesuvZ-5gOhCcrvhYr_xdSalYqI8' if IS_DEBUG else '6037063888:AAHVm-IjLif82Wt-CNykhrRU3VsJqtecjYI'
CHAT_URL = 'https://t.me/+vQm5jYWTWo1iZmMy'
telebot = _telebot.TeleBot(AUTHENTICATION_TOKEN)


def main():
    bot_config = BotConfig()

    @telebot.message_handler(commands=['start'])
    def start(message):
        print_log(f'{message.chat.id} run bot')
        telebot.send_message(message.chat.id, f'Привіт. Ми раді, що ти завітав до нас 🙂\nНаш чат: {CHAT_URL}')
        bot_config.home(message)

    @telebot.message_handler(func=lambda message: True)
    def handle_exchange_button_click(message):
        if str(message.chat.id) in ADMIN_ID_LIST:
            if 'Пеєр для обміну:' in message.text and len(message.text) > 16:
                set_payeer_account(message.text.split(':')[1].replace(' ', ''))
                telebot.send_message(message.chat.id, 'Виконано')
            elif 'Курс з пеєра долар на карту гривню:' in message.text and len(message.text) > 34:
                set_payeer_usd_to_uah_course(message.text.split(':')[1].replace(' ', ''))
                telebot.send_message(message.chat.id, 'Виконано')

        if message.text == 'Головна':
            bot_config.home(message)
        elif message.text == 'Payeer USD\n' + 'Карта UAH':
            bot_config.exchange_payeer_usd_to_uah(message)
        elif message.text == 'Реферали':
            bot_config.refferals(message)
        elif message.text == 'Курс обміну':
            bot_config.course(message)
        elif message.text == 'Підтримка':
            bot_config.support(message)

    @telebot.message_handler(content_types=['photo'])
    def handle_photo(message):
        photo = message.photo[-1]
        photo_id = photo.file_id
        chat_id = -993312734 if IS_DEBUG else -1001749858927

        if message.caption:
            telebot.send_photo(chat_id, photo_id, caption=f'id: {message.chat.id}\n{message.caption}')
            telebot.send_message(message.chat.id, f'Заявку прийнято. Обмін відбудеться протягом 48 годин❗️',
                                 reply_markup=bot_config.back_markup)
        else:
            telebot.send_message(message.chat.id, 'Виконуйте інструкцію❗️')

    telebot.polling()


class BotConfig:
    back_markup = types.ReplyKeyboardMarkup(row_width=1)
    home_markup = types.ReplyKeyboardMarkup(row_width=2)
    back_markup.add(
        types.KeyboardButton('Головна'),
    )

    home_markup.add(
        types.KeyboardButton('Payeer USD\n' + 'Карта UAH'),
        types.KeyboardButton('Реферали'),
        types.KeyboardButton('Курс обміну'),
        types.KeyboardButton('Підтримка'),
    )

    def __init__(self):
        pass

    def refferals(self, message):
        telebot.send_message(message.chat.id, 'Реферали', reply_markup=self.back_markup)

    def home(self, message):
        telebot.send_message(message.chat.id, 'Ви на головній!', reply_markup=self.home_markup)

    def exchange_payeer_usd_to_uah(self, message):
        config = get_config()

        telebot.send_message(message.chat.id,
                             f'❗️❗️❗️УВАГА❗️❗️❗️\nУ разі невиконання інструкцій адміністрація має право не проводити '
                             f'Вам обмін')
        telebot.send_message(message.chat.id,
                             f'Відправте суму для обміну на {config["payeer_account"]} від 0.2$ з коментарем: ' +
                             f'Ваша_карта Ваш_нік')
        telebot.send_message(message.chat.id, f'Надішліть скрін переказу в бот з коментарем під ним. ' +
                             f'Лише після цього заявку буде прийнято на розгляд',
                             reply_markup=self.back_markup)

    def course(self, message):
        telebot.send_message(message.chat.id, f'Курс на {datetime.now().strftime("%Y.%m.%d")}\n' +
                             f'1 Payeer USD ➡️ {get_config()["payeer_usd_to_uah"]} UAH', reply_markup=self.back_markup)

    def support(self, message):
        telebot.send_message(message.chat.id,
                             f'Контакти для отриманя підтримки: @arobotok202118 та @systnager',
                             reply_markup=self.back_markup)


if __name__ == '__main__':
    while True:
        try:
            main()
        except (ReadTimeout, ConnectionError):
            print_log("Error with Internet connection")
            time.sleep(1)
            continue
