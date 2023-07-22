import random
import time

import telebot as _telebot
from requests.exceptions import ReadTimeout, ConnectionError
from telebot import types

from business import *

ADMIN_ID_LIST = [
    '616356243',
    '1760269999',
]
IS_DEBUG = True
AUTHENTICATION_TOKEN = '6392565799:AAFzQy4uesuvZ-5gOhCcrvhYr_xdSalYqI8' if IS_DEBUG else '6037063888:AAHVm-IjLif82Wt-CNykhrRU3VsJqtecjYI'
CHAT_URL = 'https://t.me/+vQm5jYWTWo1iZmMy'
telebot = _telebot.TeleBot(AUTHENTICATION_TOKEN)


def main():
    bot_config = BotConfig()

    @telebot.message_handler(commands=['start'])
    def start(message):
        telebot.send_message(message.chat.id, f'Привіт. Ми раді, що ти завітав до нас 🙂\nНаш чат: {CHAT_URL}')
        user_id = str(message.chat.id)
        config = get_config()
        if (not (user_id in config["users"])) or config["users"][user_id]["state"] == 'register':
            telebot.send_message(message.chat.id, 'Введіть айді того, хто запросив Вас, або None')
            config["users"][user_id] = {
                "state": "register",
                "balance": 0,
                "invited_by": '',
                "invited_user_count": 0,
            }
            save_config(config)
        else:
            bot_config.home(message)

    @telebot.message_handler(func=lambda message: True)
    def handle_exchange_button_click(message):
        config = get_config()
        user_id = str(message.chat.id)
        user_text_answer = message.text

        if user_id in config["users"]:
            if config["users"][user_id]["state"] == 'register':
                if user_text_answer.isdigit() and user_text_answer in config["users"]:
                    telebot.send_message(message.chat.id, 'Чудово, реєстрацію завершено успішно!',
                                         reply_markup=bot_config.home_markup)
                    telebot.send_message(int(user_text_answer), f'У вас новий реферал з ID {user_id}')
                    config["users"][user_id]["state"] = 'default'
                    config["users"][user_id]["invited_by"] = user_text_answer
                    config["users"][user_text_answer]["invited_user_count"] += 1
                    save_config(config)
                if user_text_answer.lower() == 'none':
                    random_admin_id = random.choice(ADMIN_ID_LIST)
                    telebot.send_message(message.chat.id, 'Вам автоматично надано реферера',
                                         reply_markup=bot_config.home_markup)
                    telebot.send_message(int(random_admin_id), f'У вас новий реферал з ID {user_id}')
                    config["users"][user_id]["state"] = 'default'
                    config["users"][user_id]["invited_by"] = random_admin_id
                    config["users"][random_admin_id]["invited_user_count"] += 1
                    save_config(config)
                else:
                    telebot.send_message(message.chat.id, 'Потрібно пройти реєстрацію. ' +
                                         'Введіть айді того, хто запросив Вас, або None')

            elif message.text == 'Головна':
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
                    telebot.send_message(message.chat.id, 'Ви в адмінці', reply_markup=bot_config.admin_markup)
                else:
                    telebot.send_message(message.chat.id, 'Ви не адмін. Доступ заборонено!')

            if user_id in ADMIN_ID_LIST:
                config = get_config()
                if config["users"][user_id]["state"] == 'withdraw':
                    bot_config.get_request_for_withdrawal(message)
                elif config["users"][user_id]["state"] == 'confirm_withdraw':
                    bot_config.confirm_withdraw(message)
                elif config["users"][user_id]["state"] == 'confirm_exchange':
                    bot_config.confirm_exchange(message)
                elif config["users"][user_id]["state"] == 'change_payeer_usd_to_uah_course':
                    bot_config.change_payeer_usd_to_uah_course(message)
                elif config["users"][user_id]["state"] == 'change_payeer_account':
                    bot_config.change_payeer_account(message)
                elif config["users"][user_id]["state"] == 'send_allert_for_all_users':
                    bot_config.send_allert_for_all_users(message)

                elif message.text == 'Підтвердити виплату':
                    config["users"][user_id]["state"] = 'confirm_withdraw'
                    save_config(config)
                    telebot.send_message(message.chat.id, 'Введіть ID користувача та суму, що була виплачена в грн',
                                         reply_markup=bot_config.back_markup)
                elif message.text == 'Підтвердити обмін':
                    config["users"][user_id]["state"] = 'confirm_exchange'
                    save_config(config)
                    telebot.send_message(message.chat.id, 'Введіть ID користувача та суму, що була обміняна в грн',
                                         reply_markup=bot_config.back_markup)
                elif message.text == 'Змінити курс Payeer USD карта UAH':
                    config["users"][user_id]["state"] = 'change_payeer_usd_to_uah_course'
                    save_config(config)
                    telebot.send_message(message.chat.id, 'Введіть курс з двома знаками після коми',
                                         reply_markup=bot_config.back_markup)
                elif message.text == 'Змінити Payeer':
                    config["users"][user_id]["state"] = 'change_payeer_account'
                    save_config(config)
                    telebot.send_message(message.chat.id, 'Введіть Payeer аккаунт',
                                         reply_markup=bot_config.back_markup)
                elif message.text == 'Відправити всім користувачам сповіщення':
                    config["users"][user_id]["state"] = 'send_allert_for_all_users'
                    save_config(config)
                    telebot.send_message(message.chat.id, 'Введіть текст сповіщення',
                                         reply_markup=bot_config.back_markup)

        else:
            telebot.send_message(message.chat.id, 'Потрібно пройти реєстрацію. Натисніть /start')

    @telebot.message_handler(content_types=['photo'])
    def handle_photo(message):
        user_id = str(message.chat.id)
        config = get_config()
        if user_id in config["users"]:
            photo = message.photo[-1].file_id
            chat_id = -993312734 if IS_DEBUG else -1001749858927

            if message.caption:
                telebot.send_photo(chat_id, photo, caption=f'id юзера: {message.chat.id}\n' +
                                                           f'комент юзера: {message.caption}\n' +
                                                           f'username: @{message.from_user.username}\n' +
                                                           f'ім\'я юзера: {message.from_user.first_name}\n' +
                                                           f'рефер юзера: {config["users"][user_id]["invited_by"]}')
                telebot.send_message(message.chat.id, f'Заявку прийнято. Обмін відбудеться протягом 48 годин❗️',
                                     reply_markup=bot_config.back_markup)
            else:
                telebot.send_message(message.chat.id, 'Виконуйте інструкцію❗️')

    telebot.polling()


class BotConfig:
    home_button = types.KeyboardButton('Головна')
    payeer_usd_to_uah_button = types.KeyboardButton('Payeer USD\n' + 'Карта UAH')
    refferals_button = types.KeyboardButton('Реферали')
    course_button = types.KeyboardButton('Курс обміну')
    support_button = types.KeyboardButton('Підтримка')
    withdraw_button = types.KeyboardButton('Вивести')
    admin_options_button = types.KeyboardButton('Адмінка')
    admin_confirm_withdraw_button = types.KeyboardButton('Підтвердити виплату')
    admin_confirm_exchange_button = types.KeyboardButton('Підтвердити обмін')
    admin_change_payeer_usd_to_uah_course_button = types.KeyboardButton('Змінити курс Payeer USD карта UAH')
    admin_change_payeer_account_button = types.KeyboardButton('Змінити Payeer')
    admin_send_alert_for_all_users_button = types.KeyboardButton('Відправити всім користувачам сповіщення')

    back_markup = types.ReplyKeyboardMarkup(row_width=1)
    home_markup = types.ReplyKeyboardMarkup(row_width=2)
    admin_markup = types.ReplyKeyboardMarkup(row_width=2)
    refferals_markup = types.ReplyKeyboardMarkup(row_width=2)
    back_markup.add(
        home_button,
    )

    home_markup.add(
        payeer_usd_to_uah_button,
        refferals_button,
        course_button,
        support_button,
        admin_options_button,
    )

    refferals_markup.add(
        withdraw_button,
        home_button
    )

    admin_markup.add(
        admin_confirm_withdraw_button,
        admin_confirm_exchange_button,
        admin_change_payeer_usd_to_uah_course_button,
        admin_change_payeer_account_button,
        admin_send_alert_for_all_users_button,
        home_button,
    )

    def __init__(self):
        pass

    def refferals(self, message):
        config = get_config()
        telebot.send_message(message.chat.id,
                             f'Ваш баланс: {round(float(config["users"][str(message.chat.id)]["balance"]), 2)}грн\n' +
                             f'Усього запрошено: {config["users"][str(message.chat.id)]["invited_user_count"]}\n' +
                             f'Ваш ID для запрошення: {message.chat.id}\n' +
                             f'Ви будете отримувати 0.5% від суми обміну Ваших рефералів',
                             reply_markup=self.refferals_markup)

    def get_request_for_withdrawal(self, message):
        config = get_config()
        is_answer_valid = True
        user_id = str(message.chat.id)
        user_answer = message.text
        user_balance = float(config["users"][str(message.chat.id)]["balance"])
        if len(user_answer.split()) == 2:
            card_number, withdraw_money = user_answer.split()
            withdraw_money = withdraw_money.replace(' ', '')
            card_number = card_number.replace(' ', '')
            if len(card_number) == 16:
                try:
                    int(card_number)
                except ValueError:
                    is_answer_valid = False
                    telebot.send_message(message.chat.id, 'Номер карти може складатися лише з 16 цифр',
                                         reply_markup=self.back_markup)

                try:
                    float(withdraw_money)
                except ValueError:
                    is_answer_valid = False
                    telebot.send_message(message.chat.id, 'Введено не число на місці суми для виводу',
                                         reply_markup=self.back_markup)

                if is_answer_valid:
                    if float(withdraw_money) < 15:
                        telebot.send_message(message.chat.id,
                                             f'Сума менше 15грн❗️',
                                             reply_markup=self.back_markup)
                    elif float(withdraw_money) <= user_balance:
                        chat_id = -993312734 if IS_DEBUG else -1001749858927
                        config["users"][user_id]["balance"] = round(user_balance, 2) - round(float(withdraw_money), 2)
                        telebot.send_message(chat_id, f'id: {message.chat.id}\n' +
                                             f'{card_number} {round(float(withdraw_money), 2)}грн ' +
                                             f'@{message.from_user.username} {message.from_user.first_name}')
                        telebot.send_message(message.chat.id,
                                             f'Заявку прийнято. Виплата {round(float(withdraw_money), 2)}грн ' +
                                             f'відбудеться протягом 48 годин❗️',
                                             reply_markup=self.back_markup)
                    else:
                        telebot.send_message(message.chat.id,
                                             f'Недостатня сума для виводу на балансі❗️',
                                             reply_markup=self.back_markup)
            else:
                telebot.send_message(message.chat.id, 'Номер карти може складатися лише з 16 цифр',
                                     reply_markup=self.back_markup)
        else:
            telebot.send_message(message.chat.id, 'Некоректний запис даних для виводу',
                                 reply_markup=self.back_markup)
        save_config(config)

    def withdraw(self, message):
        config = get_config()
        config["users"][str(message.chat.id)]["state"] = 'withdraw'
        save_config(config)
        telebot.send_message(message.chat.id, 'Введіть номер карти + суму для виводу від 15грн',
                             reply_markup=self.back_markup)

    def confirm_withdraw(self, message):
        user_answer = message.text
        config = get_config()
        if len(user_answer.split()) == 2:
            user_id, withdraw_sum = user_answer.split()
            user_id = user_id.replace(' ', '')
            try:
                float(withdraw_sum)
            except ValueError:
                telebot.send_message(message.chat.id, 'Некоректно вказано суму виплати', reply_markup=self.back_markup)

            if user_id in config["users"]:
                telebot.send_message(message.chat.id, 'Виплату успішно підтверджено', reply_markup=self.back_markup)
                telebot.send_message(int(user_id), f'Ваша заявка на виплату {withdraw_sum}грн виконана')
            else:
                telebot.send_message(message.chat.id, 'Користувача не знайдено', reply_markup=self.back_markup)
        else:
            telebot.send_message(message.chat.id, 'Некоректний запис', reply_markup=self.back_markup)
        save_config(config)

    def confirm_exchange(self, message):
        user_answer = message.text
        config = get_config()
        if len(user_answer.split()) == 2:
            user_id, withdraw_sum = user_answer.split()
            user_id = user_id.replace(' ', '')
            try:
                float(withdraw_sum)
            except ValueError:
                telebot.send_message(message.chat.id, 'Некоректно вказано суму обміну', reply_markup=self.back_markup)

            if user_id in config["users"]:
                refer_balance = float(config["users"][config["users"][user_id]["invited_by"]]["balance"])
                config["users"][config["users"][user_id]["invited_by"]][
                    "balance"] = refer_balance + float(round(float(withdraw_sum) * 0.005, 2))
                telebot.send_message(message.chat.id, 'Обмін успішно підтверджено', reply_markup=self.back_markup)
                telebot.send_message(int(user_id), f'Ваша заявка на обмін {withdraw_sum}грн виконана')
            else:
                telebot.send_message(message.chat.id, 'Користувача не знайдено', reply_markup=self.back_markup)
        else:
            telebot.send_message(message.chat.id, 'Некоректний запис', reply_markup=self.back_markup)
        save_config(config)

    def change_payeer_usd_to_uah_course(self, message):
        user_answer = message.text
        try:
            float(user_answer)
        except ValueError:
            telebot.send_message(message.chat.id, 'Введено не число', reply_markup=self.back_markup)
            return

        set_payeer_usd_to_uah_course(round(float(user_answer), 2))
        telebot.send_message(message.chat.id, f'Курс {round(float(user_answer), 2)} встановлено',
                             reply_markup=self.back_markup)

    def change_payeer_account(self, message):
        payeer_account = message.text
        set_payeer_account(payeer_account)
        telebot.send_message(message.chat.id, 'Акаунт для обміну змінено', reply_markup=self.back_markup)

    def send_allert_for_all_users(self, message):
        config = get_config()
        save_config(config)

        for user_id in map(int, list(config["users"].keys())):
            telebot.send_message(user_id, message.text)

        telebot.send_message(message.chat.id, 'Повідомлення відправлено всім користувачам бота',
                             reply_markup=self.back_markup)

    def home(self, message):
        config = get_config()
        config["users"][str(message.chat.id)]["state"] = 'default'
        save_config(config)
        telebot.send_message(message.chat.id, 'Ви на головній!', reply_markup=self.home_markup)

    def exchange_payeer_usd_to_uah(self, message):
        config = get_config()

        telebot.send_message(message.chat.id,
                             f'❗️❗️❗️УВАГА❗️❗️❗️\nУ разі невиконання інструкцій адміністрація має право не проводити '
                             f'Вам обмін')
        telebot.send_message(message.chat.id,
                             f'Відправте суму для обміну на {config["payeer_account"]} від 0.2$ з коментарем: ' +
                             f'Ваша_карта {message.from_user.id} ' +
                             f'@{message.from_user.username} {message.from_user.first_name}')
        telebot.send_message(message.chat.id, f'Надішліть скрін переказу в бот з коментарем під ним. ' +
                             f'Лише після цього заявку буде прийнято на розгляд',
                             reply_markup=self.back_markup)

    def course(self, message):
        config = get_config()
        telebot.send_message(message.chat.id, f'Курс на {datetime.now().strftime("%Y.%m.%d")}\n' +
                             f'1 Payeer USD ➡️ {config["payeer_usd_to_uah"]} UAH', reply_markup=self.back_markup)

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
