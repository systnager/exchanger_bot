import random
import time
import os

import telebot
from dotenv import load_dotenv
from requests.exceptions import ReadTimeout, ConnectionError

from bot import BotConfig
from business import *
from database import get_item, update_item, write_new_item

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
        user = get_item('user', '*', ['id', [user_id]])[0]

        ref_id = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else None
        if not user:
            write_new_item('user', ['id', 'state', 'balance'], [user_id, 'default', 0])
            ref = get_item('user', '*', ['id'], [ref_id])[0]
            if ref:
                update_item('user', ['invited_by'], [ref_id], ['id'], [user_id])
                bot.send_message(int(ref_id), f'У Вас новий реферал з ID: {user_id}')
            else:
                admin_id = random.choice(ADMIN_ID_LIST)
                update_item('user', ['invited_by'], [admin_id],
                            ['id'], [user_id])
                bot.send_message(int(admin_id), f'Вам приєднано вільного реферала з ID: {user_id} як адміну')

        bot_config.home(message)

    @bot.message_handler(func=lambda message: True)
    def handle_button_click(message):
        user_id = message.chat.id
        user = get_item('user', '*', ['id'], [user_id])

        if user:
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
            elif message.text == 'Вивести':
                bot_config.withdraw(message)
            elif message.text == 'Адмінка':
                if user_id in ADMIN_ID_LIST:
                    bot.send_message(message.chat.id, 'Ви в адмінці', reply_markup=bot_config.admin_markup)
                else:
                    bot.send_message(message.chat.id, 'Ви не адмін. Доступ заборонено!')

            if user_id in ADMIN_ID_LIST:
                user = get_item('user', '*', ['id'], [user_id])
                if user:
                    user = user[0]
                    if user[1] == 'withdraw':
                        bot_config.get_request_for_withdrawal(message)
                    elif user[1] == 'confirm_withdraw':
                        bot_config.confirm_withdraw(message)
                    elif user[1] == 'confirm_exchange':
                        bot_config.confirm_exchange(message)
                    elif user[1] == 'change_payeer_usd_to_uah_course':
                        bot_config.change_payeer_usd_to_uah_course(message)
                    elif user[1] == 'change_payeer_account':
                        bot_config.change_payeer_account(message)
                    elif user[1] == 'send_allert_for_all_users':
                        bot_config.send_allert_for_all_users(message)

                    elif message.text == 'Підтвердити виплату':
                        update_item('user', ['state'], ['confirm_withdraw'], ['id'], [user_id])
                        bot.send_message(message.chat.id, 'Введіть ID користувача та суму, що була виплачена в грн, ' +
                                         f'через пробіл', reply_markup=bot_config.back_markup)
                    elif message.text == 'Підтвердити обмін':
                        update_item('user', ['state'], ['confirm_exchange'], ['id'], [user_id])
                        bot.send_message(message.chat.id, 'Введіть ID користувача та суму, що була обміняна в грн, ' +
                                         f'через пробіл', reply_markup=bot_config.back_markup)
                    elif message.text == 'Змінити курс Payeer USD карта UAH':
                        update_item('user', ['state'], ['change_payeer_usd_to_uah_course'], ['id'], [user_id])
                        bot.send_message(message.chat.id, 'Введіть курс Payeer - UAH до 4 знаків після коми',
                                         reply_markup=bot_config.back_markup)
                    elif message.text == 'Змінити Payeer':
                        update_item('user', ['state'], ['change_payeer_account'], ['id'], [user_id])
                        bot.send_message(message.chat.id, 'Введіть новий Payeer аккаунт',
                                         reply_markup=bot_config.back_markup)
                    elif message.text == 'Відправити всім користувачам сповіщення':
                        update_item('user', ['state'], ['send_allert_for_all_users'], ['id'], [user_id])
                        bot.send_message(message.chat.id, 'Введіть текст сповіщення',
                                         reply_markup=bot_config.back_markup)

        else:
            bot.send_message(message.chat.id, 'Потрібно пройти реєстрацію. Натисніть /start')

    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        user_id = message.chat.id
        config = get_config()
        user = get_item('user', '*', ['id'], [user_id])
        if user:
            photo = message.photo[-1].file_id

            if message.caption:
                bot.send_photo(CHAT_ID, photo, caption=f'курс: {config["payeer_usd_to_uah"]}\n' +
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
