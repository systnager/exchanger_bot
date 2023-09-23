import random
import time

import telebot
import mysql.connector
from requests.exceptions import ReadTimeout, ConnectionError
from telebot import types

from business import *

conn = mysql.connector.connect(
    host='161.97.78.70',
    user='u27820_ILbFuD2aI5',
    password='MIJ=OnRB+ZfrgbGoVU2AE=KO',
    database='s27820_exchanger_bot'
)

cursor = conn.cursor()

ADMIN_ID_LIST = [
    616356243,
    1760269999,
]
IS_DEBUG = False
config = get_config()
CHAT_ID = config["DEBUG_EXCHANGE_REQUEST_CHAT_ID"] if IS_DEBUG else config["EXCHANGE_REQUEST_CHAT_ID"]
AUTHENTICATION_TOKEN = config["DEBUG_AUTHENTICATION_TOKEN"] if IS_DEBUG else config["AUTHENTICATION_TOKEN"]
CHAT_URL = 'https://t.me/+vQm5jYWTWo1iZmMy'
bot = telebot.TeleBot(AUTHENTICATION_TOKEN)


def main():
    bot_config = BotConfig()

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(message.chat.id, f'Привіт. Ми раді, що ти завітав до нас 🙂\nНаш чат: {CHAT_URL}')
        user_id = message.chat.id
        cursor.execute(f'SELECT * FROM user WHERE id = {user_id};')
        user = cursor.fetchall()[0]

        ref_id = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else None
        if not user:
            cursor.execute(f'INSERT INTO user (id, state, balance) values (' +
                           f'{user_id},' +
                           f' "default",' +
                           f' 0;')
            conn.commit()

            cursor.execute(f'SELECT * FROM user WHERE id = {ref_id};')
            ref = cursor.fetchall()[0]
            if ref:
                cursor.execute(f'UPDATE user SET invited_by = {ref_id} WHERE id = {user_id};')
                conn.commit()
                bot.send_message(int(ref_id), f'У Вас новий реферал з ID: {user_id}')
            else:
                admin_id = random.choice(ADMIN_ID_LIST)
                cursor.execute(f'UPDATE user SET invited_by = {admin_id} WHERE id = {user_id};')
                conn.commit()
                bot.send_message(int(admin_id), f'Вам приєднано вільного реферала з ID: {user_id} як адміну')

        bot_config.home(message)

    @bot.message_handler(func=lambda message: True)
    def handle_button_click(message):
        user_id = message.chat.id
        cursor.execute(f'SELECT * FROM user WHERE id = {user_id};')
        user = cursor.fetchall()[0]

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
                cursor.execute(f'SELECT * FROM user WHERE id = {user_id};')
                user = cursor.fetchall()[0]
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
                    cursor.execute(f'UPDATE user SET state = "confirm_withdraw" WHERE id = {user_id};')
                    conn.commit()
                    bot.send_message(message.chat.id, 'Введіть ID користувача та суму, що була виплачена в грн, ' +
                                     f'через пробіл', reply_markup=bot_config.back_markup)
                elif message.text == 'Підтвердити обмін':
                    cursor.execute(f'UPDATE user SET state = "confirm_exchange" WHERE id = {user_id};')
                    conn.commit()
                    bot.send_message(message.chat.id, 'Введіть ID користувача та суму, що була обміняна в грн, ' +
                                     f'через пробіл', reply_markup=bot_config.back_markup)
                elif message.text == 'Змінити курс Payeer USD карта UAH':
                    cursor.execute(f'UPDATE user SET state = "change_payeer_usd_to_uah_course" WHERE id = {user_id};')
                    conn.commit()
                    bot.send_message(message.chat.id, 'Введіть курс Payeer - UAH до 4 знаків після коми',
                                     reply_markup=bot_config.back_markup)
                elif message.text == 'Змінити Payeer':
                    cursor.execute(f'UPDATE user SET state = "change_payeer_account" WHERE id = {user_id};')
                    conn.commit()
                    bot.send_message(message.chat.id, 'Введіть новий Payeer аккаунт',
                                     reply_markup=bot_config.back_markup)
                elif message.text == 'Відправити всім користувачам сповіщення':
                    cursor.execute(f'UPDATE user SET state = "send_allert_for_all_users" WHERE id = {user_id};')
                    conn.commit()
                    bot.send_message(message.chat.id, 'Введіть текст сповіщення',
                                     reply_markup=bot_config.back_markup)

        else:
            bot.send_message(message.chat.id, 'Потрібно пройти реєстрацію. Натисніть /start')

    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        user_id = message.chat.id
        config = get_config()
        cursor.execute(f'SELECT * FROM user WHERE id = {user_id};')
        user = cursor.fetchall()[0]
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
        cursor.execute(f'SELECT * FROM user WHERE id = {message.chat.id};')
        user = cursor.fetchall()[0]

        cursor.execute(f'SELECT id FROM user WHERE invited_by = {user[0]};')
        invited_user_count = len(cursor.fetchall())

        bot.send_message(message.chat.id,
                         f'Ваш баланс: {float(user[2])} грн\n' +
                         f'Усього запрошено: {invited_user_count}\n' +
                         f'Ваш URL для запрошення: https://t.me/green_exchanger_bot?start={message.chat.id}\n' +
                         f'Ви будете отримувати {config["ref_percent"]}% від суми обміну Ваших рефералів',
                         reply_markup=self.refferals_markup)

    def get_request_for_withdrawal(self, message):
        user_id = message.chat.id
        cursor.execute(f'SELECT * FROM user WHERE id = {user_id};')
        user = cursor.fetchall()[0]
        user_answer = message.text
        print(user_answer)
        user_balance = user[2]
        if len(user_answer.split()) == 2:
            card_number, withdraw_money = user_answer.split()
            withdraw_money = withdraw_money.replace(' ', '')
            card_number = card_number.replace(' ', '')
            if len(card_number) == 16:
                try:
                    int(card_number)
                except ValueError:
                    bot.send_message(message.chat.id, 'Номер карти може складатися лише з 16 цифр',
                                     reply_markup=self.back_markup)
                    return

                try:
                    float(withdraw_money)
                except ValueError:
                    bot.send_message(message.chat.id, 'Введено не валідне значення на місці суми для виводу',
                                     reply_markup=self.back_markup)
                    return

                if float(withdraw_money) < 1:
                    bot.send_message(message.chat.id,
                                     f'Сума менше 1грн❗️',
                                     reply_markup=self.back_markup)
                elif float(withdraw_money) <= user_balance:
                    cursor.execute(f'UPDATE user SET balance = ' +
                                   f'{user[2] - round(float(withdraw_money), 2)} WHERE id = {user[0]};')
                    conn.commit()
                    bot.send_message(CHAT_ID, f'id: {message.chat.id}\n' +
                                     f'Номер карти: {card_number}\n' +
                                     f'Сума для виплати: {round(float(withdraw_money), 2)}грн\n' +
                                     f'@{message.from_user.username}')
                    bot.send_message(message.chat.id,
                                     f'Заявку прийнято. Виплата {round(float(withdraw_money), 2)}грн ' +
                                     f'відбудеться протягом 48 годин❗️',
                                     reply_markup=self.back_markup)
                else:
                    bot.send_message(message.chat.id,
                                     f'Недостатня сума для виводу на балансі❗️',
                                     reply_markup=self.back_markup)
            else:
                bot.send_message(message.chat.id, 'Номер карти може складатися лише з 16 цифр',
                                 reply_markup=self.back_markup)
        else:
            if user_answer != "Вивести":
                bot.send_message(message.chat.id, 'Невалідна команда. Введіть номер карти та суму через пробіл',
                                 reply_markup=self.back_markup)

    def withdraw(self, message):
        user_id = message.chat.id
        cursor.execute(f'UPDATE user SET state = "withdraw" WHERE id = {user_id};')
        conn.commit()
        bot.send_message(message.chat.id, 'Введіть номер карти + суму для виводу від 1грн через пробіл',
                         reply_markup=self.back_markup)

    def confirm_withdraw(self, message):
        user_answer = message.text
        if len(user_answer.split()) == 2:
            user_id, withdraw_sum = user_answer.split()
            user_id = int(user_id.replace(' ', ''))
            try:
                float(withdraw_sum)
            except ValueError:
                bot.send_message(message.chat.id, 'Некоректно вказано суму виплати', reply_markup=self.back_markup)

            cursor.execute(f'SELECT * FROM user WHERE id = {user_id};')
            user = cursor.fetchall()[0]

            if user:
                bot.send_message(message.chat.id, 'Виплату успішно підтверджено', reply_markup=self.back_markup)
                bot.send_message(user_id, f'Ваша заявка на виплату {withdraw_sum}грн виконана')
            else:
                bot.send_message(message.chat.id, 'Користувача не знайдено', reply_markup=self.back_markup)
        else:
            bot.send_message(message.chat.id, 'Невалідні данні. Введіть айді користувача та суму через пробіл',
                             reply_markup=self.back_markup)

    def confirm_exchange(self, message):
        user_answer = message.text
        config = get_config()
        if len(user_answer.split()) == 2:
            user_id, withdraw_sum = user_answer.split()
            user_id = int(user_id.replace(' ', ''))
            try:
                float(withdraw_sum)
            except ValueError:
                bot.send_message(message.chat.id, 'Некоректно вказано суму обміну', reply_markup=self.back_markup)

            cursor.execute(f'SELECT * FROM user WHERE id = {user_id};')
            user = cursor.fetchall()[0]

            if user:
                cursor.execute(f'SELECT * FROM user WHERE id = {user[3]};')
                ref = cursor.fetchall()[0]
                cursor.execute(f'UPDATE user SET balance = ' +
                               f'{ref[2] + (round(float(withdraw_sum) * (config["ref_percent"] / 100), 4))} ' +
                               f'WHERE id = {ref[0]};')
                conn.commit()
                bot.send_message(message.chat.id, 'Обмін успішно підтверджено', reply_markup=self.back_markup)
                bot.send_message(user_id, f'Ваша заявка на обмін {withdraw_sum}грн виконана')
            else:
                bot.send_message(message.chat.id, 'Користувача не знайдено', reply_markup=self.back_markup)
        else:
            bot.send_message(message.chat.id, 'Невалідні данні. Введіть айді користувача та суму через пробіл',
                             reply_markup=self.back_markup)

    def change_payeer_usd_to_uah_course(self, message):
        user_answer = message.text
        try:
            float(user_answer)
        except ValueError:
            bot.send_message(message.chat.id, 'Введено не число', reply_markup=self.back_markup)
            return

        set_payeer_usd_to_uah_course(round(float(user_answer), 2))
        bot.send_message(message.chat.id, f'Курс {round(float(user_answer), 2)} за 1$ Payeer встановлено',
                         reply_markup=self.back_markup)

    def change_payeer_account(self, message):
        payeer_account = message.text
        set_payeer_account(payeer_account)
        bot.send_message(message.chat.id, 'Payeer акаунт для обміну змінено', reply_markup=self.back_markup)

    def send_allert_for_all_users(self, message):
        cursor.execute(f'SELECT * FROM user')
        users = cursor.fetchall()

        for user in users:
            user_id = user[0]
            bot.send_message(user_id, message.text)

        bot.send_message(message.chat.id, 'Повідомлення відправлено всім користувачам бота',
                         reply_markup=self.back_markup)

    def home(self, message):
        user_id = message.chat.id
        cursor.execute(f'UPDATE user SET state = "default" WHERE id = {user_id};')
        conn.commit()
        bot.send_message(message.chat.id, 'Ви на головній!', reply_markup=self.home_markup)

    def exchange_payeer_usd_to_uah(self, message):
        config = get_config()
        bot.send_message(message.chat.id,
                         f'Відправте суму для обміну на {config["payeer_account"]} від 0.2$ з коментарем: Ваша_карта.')
        bot.send_message(message.chat.id, f'Надішліть скрін переказу в бот та в описі до фото введіть номер карти, ' +
                         f'лише після цього заявку буде прийнято на розгляд. Максимальний термін обміну - 48 годин',
                         reply_markup=self.back_markup)

    def course(self, message):
        config = get_config()
        bot.send_message(message.chat.id, f'Курс на {datetime.now().strftime("%Y.%m.%d")}\n' +
                         f'1 Payeer USD ➡️ {config["payeer_usd_to_uah"]} UAH', reply_markup=self.back_markup)

    def support(self, message):
        bot.send_message(message.chat.id,
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
