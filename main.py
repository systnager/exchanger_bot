import random
import time
import os

import telebot
from dotenv import load_dotenv
from requests.exceptions import ReadTimeout, ConnectionError

from bot import BotConfig
from business import *
from database import get_item, update_item, write_new_item
from mysql.connector.errors import OperationalError

load_dotenv()
ADMIN_ID_LIST = [
    616356243,
    1760269999,
]
IS_DEBUG = True if os.getenv('IS_DEBUG') == "True" else False
CHAT_ID = os.getenv('DEBUG_EXCHANGE_REQUEST_CHAT_ID') if IS_DEBUG else os.getenv('EXCHANGE_REQUEST_CHAT_ID')
AUTHENTICATION_TOKEN = os.getenv('DEBUG_AUTHENTICATION_TOKEN') if IS_DEBUG else os.getenv('AUTHENTICATION_TOKEN')
CHAT_URL = 'https://t.me/+vQm5jYWTWo1iZmMy'
bot = telebot.TeleBot(AUTHENTICATION_TOKEN)


def main():
    bot_config = BotConfig(bot)

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(message.chat.id, f'Привіт. Ми раді, що ти завітав до нас 🙂\nНаш чат: {CHAT_URL}')
        user_id = message.chat.id
        user = get_item('user', '*', ['id'], [user_id])
        ref_id = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else random.choice(ADMIN_ID_LIST)
        if not user:
            write_new_item('user', ['id', 'state', 'balance'], [user_id, 'default', 0])
            ref = get_item('user', '*', ['id'], [ref_id])
            if ref:
                if ref_id in ADMIN_ID_LIST:
                    update_item('user', ['invited_by'], [ref_id],
                                ['id'], [user_id])
                    bot.send_message(int(ref_id), f'Вам приєднано вільного реферала з ID: {user_id} як адміну')
                else:
                    update_item('user', ['invited_by'], [ref_id], ['id'], [user_id])
                    bot.send_message(int(ref_id), f'У Вас новий реферал з ID: {user_id}')
            else:
                bot.send_message(message.chat.id, f'Вас НЕ приєднано до реферера')

        bot_config.home(message)

    @bot.message_handler(func=lambda message: True)
    def handle_button_click(message):
        user_id = message.chat.id
        user = get_item('user', '*', ['id'], [user_id])

        action = {
            'Головна': lambda: bot_config.home(message),
            'Payeer USD\n' + 'Карта UAH': lambda: bot_config.exchange_payeer_usd_to_uah(message),
            'Реферали': lambda: bot_config.refferals(message),
            'Курс обміну': lambda: bot_config.course(message),
            'Підтримка': lambda: bot_config.support(message),
            'Вивести': lambda: bot_config.withdraw(message),
        }

        admin_action = {
            'Адмінка': lambda: bot.send_message(message.chat.id, 'Ви в адмінці', reply_markup=bot_config.admin_markup),
            'Підтвердити виплату': lambda: bot_config.set_confirm_withdraw_state(message),
            'Підтвердити обмін': lambda: bot_config.set_confirm_exchange_state(message),
            'Змінити курс Payeer USD карта UAH': lambda: bot_config.set_change_payeer_usd_to_uah_course_state(message),
            'Змінити Payeer': lambda: bot_config.set_change_payeer_account_state(message),
            'Відправити всім користувачам сповіщення': lambda: bot_config.set_send_allert_for_all_users_state(message),

            'withdraw': lambda: bot_config.get_request_for_withdrawal(message),
            'confirm_withdraw': lambda: bot_config.confirm_withdraw(message),
            'confirm_exchange': lambda: bot_config.confirm_exchange(message),
            'change_payeer_usd_to_uah_course': lambda: bot_config.change_payeer_usd_to_uah_course(message),
            'change_payeer_account': lambda: bot_config.change_payeer_account(message),
            'send_allert_for_all_users': lambda: bot_config.send_allert_for_all_users(message),
        }

        if user:
            if message.text in action:
                action[message.text]()
            if user_id in ADMIN_ID_LIST:
                user = get_item('user', '*', ['id'], [user_id])
                user = user[0]
                if message.text in admin_action:
                    admin_action[message.text]()
                elif user[1] in admin_action:
                    admin_action[user[1]]()
        else:
            bot.send_message(message.chat.id, 'Потрібно пройти реєстрацію. Натисніть /start')

    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        user_id = message.chat.id
        payeer_usd_to_uah = get_item('settings', ['payeer_usd_to_uah'], ['id'], [1])[0][0]
        user = get_item('user', '*', ['id'], [user_id])
        if user and message.caption:
            photo = message.photo[-1].file_id
            bot.send_photo(CHAT_ID, photo, caption=f'курс: {payeer_usd_to_uah}\n' +
                                                   f'id юзера: {message.chat.id}\n' +
                                                   f'комент юзера: {message.caption}\n' +
                                                   f'username: @{message.from_user.username}\n')

            bot.send_message(message.chat.id, f'Заявку прийнято. Обмін відбудеться протягом 48 годин❗️',
                             reply_markup=bot_config.back_markup)
        else:
            bot.send_message(message.chat.id, 'Заявку НЕ прийнято. Виконуйте інструкцію❗️')

    bot.polling()


if __name__ == '__main__':
    while True:
        try:
            main()
        except (ReadTimeout, ConnectionError):
            print_log("Error with Internet connection")
            time.sleep(1)
            continue
        except OperationalError:
            print_log("Error with connection to database")
            time.sleep(1)
            continue
