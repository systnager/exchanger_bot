import os
import random

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

from business import *

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
    home_button = KeyboardButton(text='Головна')
    payeer_usd_to_uah_button = KeyboardButton(text='Payeer USD\n' + 'Карта UAH')
    referrals_button = KeyboardButton(text='Реферали')
    course_button = KeyboardButton(text='Курс обміну')
    support_button = KeyboardButton(text='Підтримка')
    withdraw_button = KeyboardButton(text='Вивести')
    admin_options_button = KeyboardButton(text='Адмінка')
    admin_confirm_withdraw_button = KeyboardButton(text='Підтвердити виплату')
    admin_confirm_exchange_button = KeyboardButton(text='Підтвердити обмін')
    admin_change_payeer_usd_to_uah_course_button = KeyboardButton(text='Змінити курс Payeer USD карта UAH')
    admin_change_payeer_account_button = KeyboardButton(text='Змінити Payeer')
    admin_send_alert_for_all_users_button = KeyboardButton(text='Відправити всім користувачам сповіщення')

    back_builder = ReplyKeyboardBuilder()
    home_builder = ReplyKeyboardBuilder()
    admin_builder = ReplyKeyboardBuilder()
    referrals_builder = ReplyKeyboardBuilder()

    back_builder.row(
        home_button,
    )

    home_builder.row(
        payeer_usd_to_uah_button,
        referrals_button,
    ).row(
        course_button,
        support_button,
    ).row(
        admin_options_button,
    )

    admin_builder.row(
        admin_confirm_withdraw_button,
        admin_confirm_exchange_button,
    ).row(
        admin_change_payeer_usd_to_uah_course_button,
        admin_change_payeer_account_button,
    ).row(
        admin_send_alert_for_all_users_button,
        home_button,
    )

    referrals_builder.row(
        withdraw_button,
        home_button,
    )

    def __init__(self, database):
        self.dp = Dispatcher()
        self.bot = Bot(AUTHENTICATION_TOKEN, parse_mode=ParseMode.HTML)
        self.database = database

        @self.dp.message(CommandStart())
        async def command_start_handle(message):
            await self._command_start_handle(message)

        @self.dp.message()
        async def on_user_shared(message):
            await self._on_button_click(message)

    async def start(self):
        await self.dp.start_polling(self.bot)

    async def referrals(self, message):
        config = get_config()
        user = self.database.get_user(message.chat.id)
        if user:
            user = user[0]
            invited_user_count = self.database.get_user_referrals_count(user[0])

            await self.bot.send_message(message.from_user.id,
                                        f'Ваш ID: {user[0]}\nВаш баланс: {float(user[2]):.2f} грн\nУсього запрошено: {invited_user_count}\nВаш URL для запрошення: https://t.me/green_exchanger_bot?start={message.chat.id}\nВи будете отримувати {config["ref_percent"]}% від суми обміну Ваших рефералів',
                                        reply_markup=self.referrals_builder.as_markup(resize_keyboard=True))

    async def get_request_for_withdrawal(self, message):
        user = self.database.get_user(message.chat.id)
        if user:
            user = user[0]
            user_answer = message.text
            if len(user_answer.split()) == 2:
                card_number, withdraw_money = user_answer.split()
                withdraw_money = withdraw_money.replace(' ', '')
                card_number = card_number.replace(' ', '')
                if is_card_number_valid(card_number) and is_numeric(withdraw_money):
                    withdraw_money = float(withdraw_money)
                    await self._withdrawal_request_processing(message, user, withdraw_money, card_number)
                else:
                    await self.bot.send_message(message.from_user.id, 'Номер карти може складатися лише з 16 цифр!',
                                                reply_markup=self.back_builder.as_markup(resize_keyboard=True))
                    await self.bot.send_message(message.from_user.id, 'Сума для виводу повинна бути дійсним числом!',
                                                reply_markup=self.back_builder.as_markup(resize_keyboard=True))
            else:
                if user_answer != "Вивести":
                    await self.bot.send_message(message.from_user.id,
                                                'Невалідна команда. Введіть номер карти та суму через пробіл')
                    await self.bot.send_message(message.from_user.id,
                                                'Ось приклад, як потрібно ввести данні: 4114544287780987 1.23',
                                                reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def withdraw(self, message):
        user_id = message.chat.id
        self.database.changer_user_state(user_id, 'withdraw')
        await self.bot.send_message(message.from_user.id, 'Введіть номер карти + суму для виводу від 1грн через пробіл',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def confirm_withdraw(self, message):
        user_answer = message.text
        if len(user_answer.split()) == 2:
            user_id, withdraw_sum = user_answer.split()
            user_id = user_id.replace(' ', '')
            if not is_numeric(user_id):
                await self.bot.send_message(message.from_user.id, 'Невалідний ID користувача',
                                            reply_markup=self.back_builder.as_markup(resize_keyboard=True))
                return

            if is_numeric(withdraw_sum):
                user = self.database.get_user(user_id)
                if user:
                    await self.bot.send_message(message.from_user.id, 'Виплату успішно підтверджено',
                                                reply_markup=self.back_builder.as_markup(resize_keyboard=True))
                    await self.bot.send_message(message.from_user.id,
                                                f'Ваша заявка на виплату {withdraw_sum}грн виконана')
                else:
                    await self.bot.send_message(message.from_user.id, 'Користувача не знайдено',
                                                reply_markup=self.back_builder.as_markup(resize_keyboard=True))
            else:
                await self.bot.send_message(message.from_user.id, 'Некоректно вказано суму виплати',
                                            reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id,
                                        'Невалідні данні. Введіть айді користувача та суму через пробіл',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def confirm_exchange(self, message):
        user_answer = message.text
        config = get_config()
        if len(user_answer.split()) == 2:
            user_id, withdraw_sum = user_answer.split()
            user_id = user_id.replace(' ', '')
            if not is_numeric(user_id):
                await self.bot.send_message(message.from_user.id, 'Невалідний ID користувача',
                                            reply_markup=self.back_builder.as_markup(resize_keyboard=True))
                return
            user_id = int(user_id)
            if is_numeric(withdraw_sum):
                withdraw_sum = float(withdraw_sum)
                user = self.database.get_user(user_id)
                await self._make_exchange(message, user, withdraw_sum, config)
            else:
                await self.bot.send_message(message.from_user.id, 'Некоректно вказано суму обміну',
                                            reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id,
                                        'Невалідні данні. Введіть айді користувача та суму через пробіл',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def change_payeer_usd_to_uah_course(self, message):
        user_answer = message.text
        if is_numeric(user_answer):
            user_answer = float(user_answer)
            set_payeer_usd_to_uah_course(round(user_answer * 100) / 100)
            await self.bot.send_message(message.from_user.id, f'Курс {user_answer:.2f} за 1$ Payeer встановлено',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id, 'Введено не число',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def change_payeer_account(self, message):
        payeer_account = message.text
        set_payeer_account(payeer_account)
        await self.bot.send_message(message.from_user.id, 'Payeer акаунт для обміну змінено',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def send_alert_for_all_users(self, message):
        await self.bot.send_message(message.from_user.id, 'Зачекайте, надсилаю повідомлення',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        for user in self.database.get_users():
            user_id = user[0]
            # try:
            await self.bot.send_message(user_id, message.text)
            # except ApiTelegramException:
            #    continue
        await self.bot.send_message(message.from_user.id, 'Повідомлення відправлено всім користувачам бота',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def set_confirm_withdraw_state(self, message):
        self.database.changer_user_state(message.chat.id, 'confirm_withdraw')
        await self.bot.send_message(message.from_user.id,
                                    'Введіть ID користувача та суму, що була виплачена в грн, через пробіл',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def set_confirm_exchange_state(self, message):
        self.database.changer_user_state(message.chat.id, 'confirm_exchange')
        await self.bot.send_message(message.from_user.id,
                                    'Введіть ID користувача та суму, що була обміняна в грн, через пробіл',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def set_change_payeer_usd_to_uah_course_state(self, message):
        self.database.changer_user_state(message.chat.id, 'change_payeer_usd_to_uah_course')
        await self.bot.send_message(message.from_user.id, 'Введіть курс Payeer - UAH до 4 знаків після коми',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def set_change_payeer_account_state(self, message):
        self.database.changer_user_state(message.chat.id, 'change_payeer_account')
        await self.bot.send_message(message.from_user.id, 'Введіть новий Payeer аккаунт',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def set_send_alert_for_all_users_state(self, message):
        self.database.changer_user_state(message.chat.id, 'send_alert_for_all_users')
        await self.bot.send_message(message.from_user.id, 'Введіть текст сповіщення',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def home(self, message):
        user_id = message.chat.id
        self.database.changer_user_state(user_id, 'default')
        await self.bot.send_message(message.from_user.id, 'Ви на головній!',
                                    reply_markup=self.home_builder.as_markup(resize_keyboard=True))

    async def exchange_payeer_usd_to_uah(self, message):
        config = get_config()
        # await self.bot.send_message(message.from_user.id,
        #                             f'Відправте суму для обміну на {config["payeer_account"]} від 0.2$ з коментарем: Ваша_карта.')
        await self.bot.send_message(message.from_user.id,
                                    f'Пізніше буде додано функціонал',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def course(self, message):
        config = get_config()
        await self.bot.send_message(message.from_user.id,
                                    f'Курс на {datetime.now().strftime("%Y.%m.%d")}\n1 Payeer USD ➡️ {config["payeer_usd_to_uah"]} UAH',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def support(self, message):
        await self.bot.send_message(message.from_user.id,
                                    f'Контакти для отриманя підтримки: @systnager та systnager@ukr.net',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def _register_new_user(self, message, user_id, ref_id):
        self.database.add_new_user(user_id)
        ref = self.database.get_user(ref_id)
        if ref:
            if ref_id in ADMIN_ID_LIST:
                self.database.change_user_refer(user_id, ref_id)
                await self.bot.send_message(int(ref_id), f'Вам приєднано вільного реферала з ID: {user_id} як адміну')
            else:
                self.database.change_user_refer(user_id, ref_id)
                await self.bot.send_message(int(ref_id), f'У Вас новий реферал з ID: {user_id}')
        else:
            await self.bot.send_message(message.from_user.id, f'Вас НЕ приєднано до реферера')

    async def _make_exchange(self, message, user, withdraw_sum, config):
        if user:
            user = user[0]
            await self.bot.send_message(message.chat.id, 'Обмін успішно підтверджено',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))
            await self.bot.send_message(user[0], f'Ваша заявка на обмін {withdraw_sum}грн виконана')
            if len(user) == 4:
                ref = self.database.get_user(user[3] if user[3] is not None else 'NULL')
                if ref:
                    ref = ref[0]
                    self.database.change_user_balance(ref[0], ref[2] + round(
                        (withdraw_sum * (config["ref_percent"] / 100)) * 10 ** 4) / 10 ** 4)
        else:
            await self.bot.send_message(message.from_user.id, 'Користувача не знайдено',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def _withdrawal_request_processing(self, message, user, withdraw_money, card_number):
        user_balance = user[2]
        if withdraw_money < 1:
            await self.bot.send_message(message.from_user.id, f'Сума менше 1грн❗️',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        elif withdraw_money <= user_balance:
            self.database.change_user_balance(user[0], user[2] - (round(withdraw_money * 100) / 100))
            await self.bot.send_message(CHAT_ID,
                                        f'id: {message.chat.id}\nНомер карти: {card_number}\nСума для виплати: {withdraw_money:.2f}грн\n@{message.from_user.username}')
            await self.bot.send_message(message.from_user.id,
                                        f'Заявку прийнято. Виплата {withdraw_money:.2f}грн відбудеться протягом 48 годин❗️',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id, f'Недостатня сума для виводу на балансі❗️',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def _command_start_handle(self, message):
        await self.bot.send_message(message.from_user.id,
                                    f'Привіт. Ми раді, що ти завітав до нас 🙂\nНаш чат: {CHAT_URL}')
        user_id = message.chat.id
        user = self.database.get_user(user_id)
        ref_id = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else random.choice(ADMIN_ID_LIST)
        if not user:
            await self._register_new_user(message, user_id, ref_id)

        await self.home(message)

    async def _on_button_click(self, message):
        user_id = message.from_user.id
        user = self.database.get_user(user_id)

        user_action = {
            'Головна': lambda: self.home(message),
            'Payeer USD\nКарта UAH': lambda: self.exchange_payeer_usd_to_uah(message),
            'Реферали': lambda: self.referrals(message),
            'Курс обміну': lambda: self.course(message),
            'Підтримка': lambda: self.support(message),
            'Вивести': lambda: self.withdraw(message),
        }

        admin_action = {
            'Адмінка': lambda: self.bot.send_message(message.chat.id, 'Ви в адмінці',
                                                     reply_markup=self.admin_builder.as_markup(resize_keyboard=True)),
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
                await user_action[message.text]()
            if user_id in ADMIN_ID_LIST:
                user = self.database.get_user(user_id)
                user = user[0]
                if message.text in admin_action:
                    await admin_action[message.text]()
                elif user[1] in admin_action:
                    await admin_action[user[1]]()
        else:
            await self.bot.send_message(message.from_user.id, 'Потрібно пройти реєстрацію. Натисніть /start')
