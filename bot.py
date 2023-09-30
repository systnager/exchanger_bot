import os
import random

import telebot
from dotenv import load_dotenv
from telebot import types
from telebot.apihelper import ApiTelegramException

from business import is_numeric, get_config, set_payeer_account, set_payeer_usd_to_uah_course, is_card_number_valid, datetime

load_dotenv()
ADMIN_ID_LIST = [
    616356243,
    1760269999,
]
IS_DEBUG = True if os.getenv('IS_DEBUG') == "True" else False
CHAT_ID = os.getenv('DEBUG_EXCHANGE_REQUEST_CHAT_ID') if IS_DEBUG else os.getenv('EXCHANGE_REQUEST_CHAT_ID')
AUTHENTICATION_TOKEN = os.getenv('DEBUG_AUTHENTICATION_TOKEN') if IS_DEBUG else os.getenv('AUTHENTICATION_TOKEN')
CHAT_URL = 'https://t.me/+vQm5jYWTWo1iZmMy'


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

    def __init__(self, database):
        self.bot = telebot.TeleBot(AUTHENTICATION_TOKEN)
        self.database = database

        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.bot.send_message(message.chat.id, f'Привіт. Ми раді, що ти завітав до нас 🙂\nНаш чат: {CHAT_URL}')
            user_id = message.chat.id
            user = self.database.get_item('user', '*', {'id': user_id})
            ref_id = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else random.choice(ADMIN_ID_LIST)
            if not user:
                self._register_new_user(message, user_id, ref_id)

            self.home(message)

        @self.bot.message_handler(func=lambda message: True)
        def handle_button_click(message):
            user_id = message.chat.id
            user = self.database.get_item('user', '*', {'id': user_id})

            user_action = {
                'Головна': lambda: self.home(message),
                'Payeer USD\nКарта UAH': lambda: self.exchange_payeer_usd_to_uah(message),
                'Реферали': lambda: self.refferals(message),
                'Курс обміну': lambda: self.course(message),
                'Підтримка': lambda: self.support(message),
                'Вивести': lambda: self.withdraw(message),
            }

            admin_action = {
                'Адмінка': lambda: self.bot.send_message(message.chat.id, 'Ви в адмінці',
                                                         reply_markup=self.admin_markup),
                'Підтвердити виплату': lambda: self.set_confirm_withdraw_state(message),
                'Підтвердити обмін': lambda: self.set_confirm_exchange_state(message),
                'Змінити курс Payeer USD карта UAH': lambda: self.set_change_payeer_usd_to_uah_course_state(message),
                'Змінити Payeer': lambda: self.set_change_payeer_account_state(message),
                'Відправити всім користувачам сповіщення': lambda: self.set_send_alert_for_all_users_state(message),

                'withdraw': lambda: self.get_request_for_withdrawal(message),
                'confirm_withdraw': lambda: self.confirm_withdraw(message),
                'confirm_exchange': lambda: self.confirm_exchange(message),
                'change_payeer_usd_to_uah_course': lambda: self.change_payeer_usd_to_uah_course(message),
                'change_payeer_account': lambda: self.change_payeer_account(message),
                'send_alert_for_all_users': lambda: self.send_alert_for_all_users(message),
            }

            if user:
                if message.text in user_action:
                    user_action[message.text]()
                if user_id in ADMIN_ID_LIST:
                    user = self.database.get_item('user', '*', {'id': user_id})
                    user = user[0]
                    if message.text in admin_action:
                        admin_action[message.text]()
                    elif user[1] in admin_action:
                        admin_action[user[1]]()
            else:
                self.bot.send_message(message.chat.id, 'Потрібно пройти реєстрацію. Натисніть /start')

        @self.bot.message_handler(content_types=['photo'])
        def handle_photo(message):
            user_id = message.chat.id
            payeer_usd_to_uah = get_config()['payeer_usd_to_uah']
            user = self.database.get_item('user', '*', {'id': user_id})
            if user and message.caption:
                photo = message.photo[-1].file_id
                self.bot.send_photo(CHAT_ID, photo, caption=f'курс: {payeer_usd_to_uah}\n' +
                                                            f'id юзера: {message.chat.id}\n' +
                                                            f'комент юзера: {message.caption}\n' +
                                                            f'username: @{message.from_user.username}\n')

                self.bot.send_message(message.chat.id, f'Заявку прийнято. Обмін відбудеться протягом 48 годин❗️',
                                      reply_markup=self.back_markup)
            else:
                self.bot.send_message(message.chat.id, 'Заявку НЕ прийнято. Виконуйте інструкцію❗️')

    def start(self):
        self.bot.polling()

    def refferals(self, message):
        config = get_config()
        user = self.database.get_item('user', '*', {'id': message.chat.id})[0]

        invited_user_count = len(self.database.get_item('user', ['id'], {'invited_by': user[0]}))

        self.bot.send_message(message.chat.id,
                              f'Ваш баланс: {float(user[2])} грн\n' +
                              f'Усього запрошено: {invited_user_count}\n' +
                              f'Ваш URL для запрошення: https://t.me/green_exchanger_bot?start={message.chat.id}\n' +
                              f'Ви будете отримувати {config["ref_percent"]}% від суми обміну Ваших рефералів',
                              reply_markup=self.refferals_markup)

    def get_request_for_withdrawal(self, message):
        user_id = message.chat.id
        user = self.database.get_item('user', '*', {'id': user_id})[0]
        user_answer = message.text
        user_balance = user[2]
        if len(user_answer.split()) == 2:
            card_number, withdraw_money = user_answer.split()
            withdraw_money = withdraw_money.replace(' ', '')
            card_number = card_number.replace(' ', '')
            print(is_card_number_valid(card_number))
            if is_card_number_valid(card_number) and is_numeric(withdraw_money):
                withdraw_money = float(withdraw_money)
                if withdraw_money < 1:
                    self.bot.send_message(message.chat.id, f'Сума менше 1грн❗️', reply_markup=self.back_markup)
                elif withdraw_money <= user_balance:
                    self.database.update_item('user', {'balance': user[2] - round(withdraw_money, 2)}, {'id': user[0]})
                    self.bot.send_message(CHAT_ID, f'id: {message.chat.id}\n' +
                                          f'Номер карти: {card_number}\n' +
                                          f'Сума для виплати: {round(withdraw_money, 2)}грн\n' +
                                          f'@{message.from_user.username}')
                    self.bot.send_message(message.chat.id,
                                          f'Заявку прийнято. Виплата {round(withdraw_money, 2)}грн ' +
                                          f'відбудеться протягом 48 годин❗️',
                                          reply_markup=self.back_markup)
                else:
                    self.bot.send_message(message.chat.id,
                                          f'Недостатня сума для виводу на балансі❗️',
                                          reply_markup=self.back_markup)
            else:
                self.bot.send_message(message.chat.id, 'Номер карти може складатися лише з 16 цифр!',
                                      reply_markup=self.back_markup)
                self.bot.send_message(message.chat.id, 'Сума для виводу повинна бути дійсним числом!',
                                      reply_markup=self.back_markup)
        else:
            if user_answer != "Вивести":
                self.bot.send_message(message.chat.id, 'Невалідна команда. Введіть номер карти та суму через пробіл')
                self.bot.send_message(message.chat.id, 'Ось приклад, як потрібно ввести данні: 4114544287780987 1.23',
                                      reply_markup=self.back_markup)

    def withdraw(self, message):
        user_id = message.chat.id
        self.database.update_item('user', {'state': 'withdraw'}, {'id': user_id})
        self.bot.send_message(message.chat.id, 'Введіть номер карти + суму для виводу від 1грн через пробіл',
                              reply_markup=self.back_markup)

    def confirm_withdraw(self, message):
        user_answer = message.text
        if len(user_answer.split()) == 2:
            user_id, withdraw_sum = user_answer.split()
            user_id = int(user_id.replace(' ', ''))
            if is_numeric(withdraw_sum):
                user = self.database.get_item('user', '*', {'id': user_id})
                if user:
                    self.bot.send_message(message.chat.id, 'Виплату успішно підтверджено',
                                          reply_markup=self.back_markup)
                    self.bot.send_message(user_id, f'Ваша заявка на виплату {withdraw_sum}грн виконана')
                else:
                    self.bot.send_message(message.chat.id, 'Користувача не знайдено', reply_markup=self.back_markup)
            else:
                self.bot.send_message(message.chat.id, 'Некоректно вказано суму виплати', reply_markup=self.back_markup)
        else:
            self.bot.send_message(message.chat.id, 'Невалідні данні. Введіть айді користувача та суму через пробіл',
                                  reply_markup=self.back_markup)

    def confirm_exchange(self, message):
        user_answer = message.text
        config = get_config()
        if len(user_answer.split()) == 2:
            user_id, withdraw_sum = user_answer.split()
            user_id = int(user_id.replace(' ', ''))
            if is_numeric(withdraw_sum):
                withdraw_sum = float(withdraw_sum)
                user = self.database.get_item('user', '*', {'id': user_id})
                if user:
                    user = user[0]
                    self.bot.send_message(message.chat.id, 'Обмін успішно підтверджено', reply_markup=self.back_markup)
                    self.bot.send_message(user_id, f'Ваша заявка на обмін {withdraw_sum}грн виконана')
                    if len(user) == 4:
                        print(user)
                        ref = self.database.get_item('user', '*', {'id': user[3] if user[3] is not None else 'NULL'})
                        if ref:
                            ref = ref[0]
                            self.database.update_item('user', {
                                'balance': ref[2] + (round(withdraw_sum * (config["ref_percent"] / 100), 4))
                            }, {'id': ref[0]})
                else:
                    self.bot.send_message(message.chat.id, 'Користувача не знайдено', reply_markup=self.back_markup)
            else:
                self.bot.send_message(message.chat.id, 'Некоректно вказано суму обміну', reply_markup=self.back_markup)
        else:
            self.bot.send_message(message.chat.id, 'Невалідні данні. Введіть айді користувача та суму через пробіл',
                                  reply_markup=self.back_markup)

    def change_payeer_usd_to_uah_course(self, message):
        user_answer = message.text
        if is_numeric(user_answer):
            user_answer = float(user_answer)
            set_payeer_usd_to_uah_course(round(user_answer, 2))
            self.bot.send_message(message.chat.id, f'Курс {round(user_answer, 2)} за 1$ Payeer встановлено',
                                  reply_markup=self.back_markup)
        else:
            self.bot.send_message(message.chat.id, 'Введено не число', reply_markup=self.back_markup)

    def change_payeer_account(self, message):
        payeer_account = message.text
        set_payeer_account(payeer_account)
        self.bot.send_message(message.chat.id, 'Payeer акаунт для обміну змінено', reply_markup=self.back_markup)

    def send_alert_for_all_users(self, message):
        self.bot.send_message(message.chat.id, 'Зачекайте, надсилаю повідомлення', reply_markup=self.back_markup)
        for user in self.database.get_item('user', '*'):
            user_id = user[0]
            try:
                self.bot.send_message(user_id, message.text)
            except ApiTelegramException:
                continue
        self.bot.send_message(message.chat.id, 'Повідомлення відправлено всім користувачам бота',
                              reply_markup=self.back_markup)

    def set_confirm_withdraw_state(self, message):
        self.database.update_item('user', {'state': 'confirm_withdraw'}, {'id': message.chat.id})
        self.bot.send_message(message.chat.id, 'Введіть ID користувача та суму, що була виплачена в грн, через пробіл',
                              reply_markup=self.back_markup)

    def set_confirm_exchange_state(self, message):
        self.database.update_item('user', {'state': 'confirm_exchange'}, {'id': message.chat.id})
        self.bot.send_message(message.chat.id, 'Введіть ID користувача та суму, що була обміняна в грн, через пробіл',
                              reply_markup=self.back_markup)

    def set_change_payeer_usd_to_uah_course_state(self, message):
        self.database.update_item('user', {'state': 'change_payeer_usd_to_uah_course'}, {'id': message.chat.id})
        self.bot.send_message(message.chat.id, 'Введіть курс Payeer - UAH до 4 знаків після коми',
                              reply_markup=self.back_markup)

    def set_change_payeer_account_state(self, message):
        self.database.update_item('user', {'state': 'change_payeer_account'}, {'id': message.chat.id})
        self.bot.send_message(message.chat.id, 'Введіть новий Payeer аккаунт', reply_markup=self.back_markup)

    def set_send_alert_for_all_users_state(self, message):
        self.database.update_item('user', {'state': 'send_alert_for_all_users'}, {'id': message.chat.id})
        self.bot.send_message(message.chat.id, 'Введіть текст сповіщення', reply_markup=self.back_markup)

    def home(self, message):
        user_id = message.chat.id
        self.database.update_item('user', {'state': 'default'}, {'id': user_id})
        self.bot.send_message(message.chat.id, 'Ви на головній!', reply_markup=self.home_markup)

    def exchange_payeer_usd_to_uah(self, message):
        config = get_config()
        self.bot.send_message(message.chat.id,
                              f'Відправте суму для обміну на {config["payeer_account"]} від 0.2$ з коментарем: Ваша_карта.')
        self.bot.send_message(message.chat.id,
                              f'Надішліть скрін переказу в бот та в описі до фото введіть номер карти, лише після цього заявку буде прийнято на розгляд. Максимальний термін обміну - 48 годин',
                              reply_markup=self.back_markup)

    def course(self, message):
        config = get_config()
        self.bot.send_message(message.chat.id,
                              f'Курс на {datetime.now().strftime("%Y.%m.%d")}\n1 Payeer USD ➡️ {config["payeer_usd_to_uah"]} UAH',
                              reply_markup=self.back_markup)

    def support(self, message):
        self.bot.send_message(message.chat.id, f'Контакти для отриманя підтримки: @arobotok202118 та @systnager',
                              reply_markup=self.back_markup)

    def _register_new_user(self, message, user_id, ref_id):
        self.database.write_new_item('user', {
            'id': user_id,
            'state': 'default',
            'balance': 0,
        })
        ref = self.database.get_item('user', '*', {'id': ref_id})
        if ref:
            if ref_id in ADMIN_ID_LIST:
                self.database.update_item('user', {'invited_by': ref_id}, {'id': user_id})
                self.bot.send_message(int(ref_id), f'Вам приєднано вільного реферала з ID: {user_id} як адміну')
            else:
                self.database.update_item('user', {'invited_by': ref_id}, {'id': user_id})
                self.bot.send_message(int(ref_id), f'У Вас новий реферал з ID: {user_id}')
        else:
            self.bot.send_message(message.chat.id, f'Вас НЕ приєднано до реферера')
