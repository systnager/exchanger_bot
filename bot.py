import os
import random

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

from aiogram.exceptions import TelegramForbiddenError

from business import *

load_dotenv()

IS_DEBUG = True if os.getenv('IS_DEBUG') == "True" else False
CHAT_ID = os.getenv('DEBUG_EXCHANGE_REQUEST_CHAT_ID') if IS_DEBUG else os.getenv('EXCHANGE_REQUEST_CHAT_ID')
AUTHENTICATION_TOKEN = os.getenv('DEBUG_AUTHENTICATION_TOKEN') if IS_DEBUG else os.getenv('AUTHENTICATION_TOKEN')
CHAT_URL = 'https://t.me/+vQm5jYWTWo1iZmMy'


class BotConfig:
    home_button = KeyboardButton(text='Головна')
    find_referral_button = KeyboardButton(text='Знайти реферала за айді')
    exchange_instruction_button = KeyboardButton(text='Інструкція по обміну')
    exchange_button = KeyboardButton(text='Обмін')
    payeer_usd_to_uah_button = KeyboardButton(text='Payeer USD\n' + 'Карта UAH')
    advcash_usd_to_uah_button = KeyboardButton(text='Advcash USD\n' + 'Карта UAH')
    cabinet_button = KeyboardButton(text='Кабінет')
    change_user_payeer_account_button = KeyboardButton(text='Змінити Payeer акаунт')
    change_user_advcash_account_button = KeyboardButton(text='Змінити Advcash акаунт')
    change_user_card_number_button = KeyboardButton(text='Змінити номер банківської карти')
    course_button = KeyboardButton(text='Курс обміну')
    support_button = KeyboardButton(text='Підтримка')
    withdraw_button = KeyboardButton(text='Вивести')
    admin_options_button = KeyboardButton(text='Адмінка')
    admin_sum_for_referral_withdraw = KeyboardButton(text='Сума для виплат рефоводам')
    admin_confirm_withdraw_button = KeyboardButton(text='Підтвердити виплату')
    admin_confirm_exchange_button = KeyboardButton(text='Підтвердити обмін')
    admin_change_payeer_usd_to_uah_course_button = KeyboardButton(text='Змінити курс Payeer USD карта UAH')
    admin_change_advcash_usd_to_uah_course_button = KeyboardButton(text='Змінити курс Advcash USD карта UAH')
    admin_change_payeer_account_button = KeyboardButton(text='Змінити Payeer')
    admin_change_advcash_account_button = KeyboardButton(text='Змінити Advcash')
    admin_send_alert_for_all_users_button = KeyboardButton(text='Відправити всім користувачам сповіщення')
    admin_send_alert_for_user_by_id_button = KeyboardButton(text='Відправити користувачу повідомлення')

    back_builder = ReplyKeyboardBuilder()
    home_builder = ReplyKeyboardBuilder()
    admin_builder = ReplyKeyboardBuilder()
    cabinet_builder = ReplyKeyboardBuilder()
    exchange_builder = ReplyKeyboardBuilder()

    back_builder.row(
        home_button,
    )

    home_builder.row(
        exchange_button,
        cabinet_button,
    ).row(
        course_button,
        support_button,
    ).row(
        admin_options_button,
    )

    exchange_builder.row(
        payeer_usd_to_uah_button,
        advcash_usd_to_uah_button,
    ).row(
        exchange_instruction_button,
        home_button,
    )

    admin_builder.row(
        admin_confirm_withdraw_button,
        admin_confirm_exchange_button,
    ).row(
        admin_change_payeer_usd_to_uah_course_button,
        admin_change_payeer_account_button,
    ).row(
        admin_send_alert_for_all_users_button,
        admin_send_alert_for_user_by_id_button,
    ).row(
        admin_change_advcash_usd_to_uah_course_button,
        admin_change_advcash_account_button,
    ).row(
        admin_sum_for_referral_withdraw,
        home_button,
    )

    cabinet_builder.row(
        withdraw_button,
        change_user_payeer_account_button,
    ).row(
        change_user_card_number_button,
        change_user_advcash_account_button,
    ).row(
        find_referral_button,
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

    def get_money_sum_count_to_referrals(self) -> int:
        money_sum = 0
        for user in self.database.get_users():
            money_sum += user[2]
        return money_sum

    async def show_sum_for_referral_withdraw(self, message):
        money_sum = self.get_money_sum_count_to_referrals()
        await self.bot.send_message(message.from_user.id, f'Сумарно всім рефоводам потрібно вивести {money_sum}UAH',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def show_exchange_instruction(self, message):
        await self.bot.send_message(message.from_user.id, '\n'.join([
            f'Для обміну коштів з одного напрямку на інший потрібно виконати наступні кроки:',
            f'1. У кабінеті зазначити свої номер карти та гаманець, з якого будете проводити обмін',
            f'2. Ознайомитися з поточним курсом',
            f'3. Обрати в боті потрібний напрямок обміну та скопіювати гаманець (можна скопіювати натиснувши на його)',
            f'4. Переказати бажану суму для обміну на скопійований гаманець',
            f'5. Відправити боту переказану суму у вигляді тексту. Наприклад, якщо це валюта USD - 12.5',
            f'6. Очікувати на оплату на вказані в кабінеті реквізити',
        ]), reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def cabinet(self, message):
        config = get_config()
        user = self.database.get_user(message.chat.id)[0]
        invited_user_count = self.database.get_user_referrals_count(user[0])

        await self.bot.send_message(message.from_user.id, '\n'.join([
            f'Ваш ID: <code>{user[0]}</code>',
            f'Ваш баланс: {float(user[2]):.2f} грн',
            f'Ваш Payeer акаунт: {user[5]}',
            f'Ваш Advcash акаунт: {user[7]}',
            f'Номер Вашої карти: {user[6]}',
            f'Усього запрошено: {invited_user_count}',
            f'Ваш URL для запрошення: <code>https://t.me/green_exchanger_bot?start={message.chat.id}</code>',
            f'Ви будете отримувати {config["ref_percent"]}% від суми обміну Ваших рефералів',
        ]), reply_markup=self.cabinet_builder.as_markup(resize_keyboard=True))

    async def exchange(self, message):
        await self.bot.send_message(message.from_user.id, f'Оберіть напрямок обміну',
                                    reply_markup=self.exchange_builder.as_markup(resize_keyboard=True))

    async def change_user_payeer_account(self, message):
        user_id = message.from_user.id
        self.database.changer_user_state(user_id, 'change_user_payeer_account_state')
        await self.bot.send_message(message.from_user.id, 'Введіть Ваш Payeer акаунт',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def change_user_advcash_account(self, message):
        user_id = message.from_user.id
        self.database.changer_user_state(user_id, 'change_user_advcash_account_state')
        await self.bot.send_message(message.from_user.id, 'Введіть Ваш Advcash USD акаунт',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def change_user_payeer_account_state(self, message):
        user_id = message.from_user.id
        if message.text:
            if message.text[0] == 'P':
                self.database.changer_user_state(user_id, 'default')
                self.database.changer_user_payeer_account(user_id, message.text)
                await self.bot.send_message(message.from_user.id, 'Ваш Payeer акаунт оновлено',
                                            reply_markup=self.back_builder.as_markup(resize_keyboard=True))
            else:
                await self.bot.send_message(message.from_user.id, 'Некоректний запис. Приклад: P12345',
                                            reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def change_user_advcash_account_state(self, message):
        user_id = message.from_user.id
        if message.text:
            if message.text[0] == 'U':
                self.database.changer_user_state(user_id, 'default')
                self.database.changer_user_advcash_account(user_id, message.text)
                await self.bot.send_message(message.from_user.id, 'Ваш Advcash акаунт оновлено',
                                            reply_markup=self.back_builder.as_markup(resize_keyboard=True))
            else:
                await self.bot.send_message(message.from_user.id, 'Некоректний запис. Приклад: U 123 456 789',
                                            reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def change_user_card_number(self, message):
        user_id = message.from_user.id
        self.database.changer_user_state(user_id, 'change_user_card_number_state')
        await self.bot.send_message(message.from_user.id, 'Введіть номер Вашої банківської карти',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def change_user_card_number_state(self, message):
        user_id = message.from_user.id
        card_number = message.text.replace(' ', '')
        if is_card_number_valid(card_number):
            self.database.changer_user_state(user_id, 'default')
            self.database.changer_user_card_number(user_id, int(card_number))
            await self.bot.send_message(message.from_user.id, 'Номер Вашої банківської карти оновлено',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id, 'Номер карти повинен складатися з 16 цифр без пробілів',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def get_request_for_withdrawal(self, message):
        user = self.database.get_user(message.chat.id)
        if user:
            user = user[0]
            card_number = user[6]
            user_answer = message.text
            withdraw_money = user_answer.replace(' ', '')
            if is_numeric(withdraw_money):
                withdraw_money = float(withdraw_money)
                await self._withdrawal_request_processing(message, user, withdraw_money, card_number)
            else:
                await self.bot.send_message(message.from_user.id, 'Номер карти може складатися лише з 16 цифр!',
                                            reply_markup=self.back_builder.as_markup(resize_keyboard=True))
                await self.bot.send_message(message.from_user.id, 'Сума для виводу повинна бути дійсним числом!',
                                            reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def withdraw(self, message):
        user_id = message.chat.id
        user = self.database.get_user(user_id)[0]
        if user[6]:
            self.database.changer_user_state(user_id, 'withdraw')
            await self.bot.send_message(message.from_user.id, 'Введіть суму для виводу від 1грн',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id, 'Спочатку потрібно ввести номер карти в кабінеті',
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

    async def change_advcash_usd_to_uah_course(self, message):
        user_answer = message.text
        if is_numeric(user_answer):
            user_answer = float(user_answer)
            set_payeer_usd_to_uah_course(round(user_answer * 100) / 100)
            await self.bot.send_message(message.from_user.id, f'Курс {user_answer} за 1$ Advcash встановлено',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id, 'Введено не число',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def change_bot_payeer_account(self, message):
        payeer_account = message.text
        set_payeer_account(payeer_account)
        await self.bot.send_message(message.from_user.id, 'Payeer акаунт для обміну змінено',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def change_bot_advcash_account(self, message):
        advcash_account = message.text
        set_advcash_account(advcash_account)
        await self.bot.send_message(message.from_user.id, 'Advcash акаунт для обміну змінено',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def send_alert_for_all_users(self, message):
        await self.bot.send_message(message.from_user.id, 'Зачекайте, надсилаю повідомлення',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        for user in self.database.get_users():
            user_id = user[0]
            try:
                await self.bot.send_message(user_id, message.text)
            except TelegramForbiddenError:
                print('user block the bot')
        await self.bot.send_message(message.from_user.id, 'Повідомлення відправлено всім користувачам бота',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def admin_send_alert_for_user_by_id(self, message):
        admin = self.database.get_user(message.from_user.id)[0]
        await self.bot.send_message(message.from_user.id, 'Введіть айді користувача та повідомлення через пробіл',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        self.database.changer_user_state(admin[0], 'admin_send_alert_for_user_by_id')

    async def admin_send_alert_for_user_by_id_state(self, message):
        admin = self.database.get_user(message.from_user.id)[0]
        if len(message.text.split()) > 1:
            user_id, message_text = message.text.split()[0], ' '.join(message.text.split()[1:])
            if is_numeric(user_id):
                user = self.database.get_user(int(user_id))
                if user:
                    user = user[0]
                    await self.bot.send_message(user[0], message_text)
                    self.database.changer_user_state(admin[0], 'default')
                    await self.bot.send_message(message.from_user.id, 'Повідомлення надіслано',
                                                reply_markup=self.back_builder.as_markup(resize_keyboard=True))
                else:
                    await self.bot.send_message(message.from_user.id, 'Користувача не знайдено',
                                                reply_markup=self.back_builder.as_markup(resize_keyboard=True))
            else:
                await self.bot.send_message(message.from_user.id, 'ID користувача введено некоректно',
                                            reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id, 'Некоректний запис. Введіть ID користувача та повідомлення через пробіл',
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

    async def exchange_payeer_usd_to_uah_state(self, message):
        config = get_config()
        exchange_sum = message.text
        user = self.database.get_user(message.from_user.id)[0]
        if is_numeric(exchange_sum):
            await self.bot.send_message(CHAT_ID, '\n'.join([
                f'PAYEER USD ➡️ Карта UAH',
                f'Курс: {config["payeer_usd_to_uah"]}',
                f'User Payeer: <code>{user[5]}</code>',
                f'User ID: <code>{user[0]}</code>',
                f'Username: <code>@{message.from_user.username}</code>',
                f'Користувач відправив: {exchange_sum}$',
                f'Номер карти: <code>{user[6]}</code>',
                f'До сплати: <code>{round(float(exchange_sum) * config["payeer_usd_to_uah"] * 100) / 100}</code> UAH',
                f'Код для підтвердження обміну: <code>{user[0]} {exchange_sum}</code>',

            ]))
            await self.bot.send_message(message.from_user.id, f'Заявку прийнято! Очікуйте надходження на вказану в профілі карту протягом 48 годин',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))
            self.database.changer_user_state(user[0], 'default')
        else:
            await self.bot.send_message(message.from_user.id,
                                        'Некоректно введено суму для обміну. Заявку НЕ прийнято',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def exchange_advcash_usd_to_uah_state(self, message):
        config = get_config()
        exchange_sum = message.text
        user = self.database.get_user(message.from_user.id)[0]
        if is_numeric(exchange_sum):
            await self.bot.send_message(CHAT_ID, '\n'.join([
                f'ADVCASH USD ➡️ Карта UAH',
                f'Курс: {config["advcash_usd_to_uah"]}',
                f'User Advcash: <code>{user[7]}</code>',
                f'User ID: <code>{user[0]}</code>',
                f'Username: <code>@{message.from_user.username}</code>',
                f'Користувач відправив: {exchange_sum}$',
                f'Номер карти: <code>{user[6]}</code>',
                f'До сплати: <code>{round(float(exchange_sum) * config["advcash_usd_to_uah"] * 100) / 100}</code> UAH',
                f'Код для підтвердження обміну: <code>{user[0]} {exchange_sum}</code>',

            ]))
            await self.bot.send_message(message.from_user.id, f'Заявку прийнято! Очікуйте надходження на вказану в профілі карту протягом 48 годин',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))
            self.database.changer_user_state(user[0], 'default')
        else:
            await self.bot.send_message(message.from_user.id,
                                        'Некоректно введено суму для обміну. Заявку НЕ прийнято',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def set_change_payeer_usd_to_uah_course_state(self, message):
        self.database.changer_user_state(message.chat.id, 'change_payeer_usd_to_uah_course')
        await self.bot.send_message(message.from_user.id, 'Введіть курс Payeer USD - UAH до 4 знаків після коми',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def set_change_advcash_usd_to_uah_course_state(self, message):
        self.database.changer_user_state(message.chat.id, 'change_advcash_usd_to_uah_course')
        await self.bot.send_message(message.from_user.id, 'Введіть курс Advcash USD - UAH до 4 знаків після коми',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def set_change_payeer_account_state(self, message):
        self.database.changer_user_state(message.chat.id, 'change_payeer_account')
        await self.bot.send_message(message.from_user.id, 'Введіть новий Payeer аккаунт',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def set_change_advcash_account_state(self, message):
        self.database.changer_user_state(message.chat.id, 'change_advcash_account')
        await self.bot.send_message(message.from_user.id, 'Введіть новий Advcash аккаунт',
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
        user = self.database.get_user(message.from_user.id)[0]
        if user[5] and user[6]:
            self.database.changer_user_state(user[0], 'exchange_payeer_usd_to_uah_state')
            await self.bot.send_message(message.from_user.id,'\n'.join([
                f'1. Відправте кошти на гаманець <code>{config["payeer_account"]}</code> від 0.2$',
                f'2. До платежу додайте коментар: <code>id: {message.from_user.id} card: {user[6]}</code>',
                f'3. Після переказу коштів введіть у чат боту суму відправлених коштів, що Ви надіслали',
                f'Увага, усі данні в кабінеті (номер карти, ваші гаманці) повинні бути валідними!',
                f'В іншому випадку адміністрація залишає за собою право відмовити у виплаті без жодних відшкодувань!',
                f'Якщо Ви НЕ отримали сповіщення про те, що заявка прийнята чи ні, надішліть її знову',
                f'Іноді є проблеми на стороні хостинга з інтернетом, тому іноді бот може не відповідати короткий термін часу',
            ]), reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id, f'Будь ласка, зазначте номер Вашої карти та Ваш Payeer акаунт у кабінеті',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def find_referral(self, message):
        self.database.changer_user_state(message.chat.id, 'find_referral_state')
        await self.bot.send_message(message.from_user.id, 'Введіть ID шуканого користувача',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def find_referral_state(self, message):
        user_id = message.chat.id
        referral_id = message.text
        self.database.changer_user_state(user_id, 'default')
        referral = self.database.get_user(referral_id)
        if referral:
            if user_id == referral[0][3]:
                await self.bot.send_message(message.from_user.id, 'Користувач є Вашим рефералом 😇',
                                            reply_markup=self.home_builder.as_markup(resize_keyboard=True))
            else:

                await self.bot.send_message(message.from_user.id, 'Такого користувача немає у списку Ваших рефералів 😞',
                                            reply_markup=self.home_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id, 'Такого користувача у нас поки немає 😞',
                                        reply_markup=self.home_builder.as_markup(resize_keyboard=True))

    async def exchange_advcash_usd_to_uah(self, message):
        config = get_config()
        user = self.database.get_user(message.from_user.id)[0]
        if user[5] and user[6]:
            self.database.changer_user_state(user[0], 'exchange_advcash_usd_to_uah_state')
            await self.bot.send_message(message.from_user.id,'\n'.join([
                f'1. Відправте кошти на гаманець <code>{config["advcash_account"]}</code> від 0.2$',
                f'2. До платежу додайте коментар: <code>id: {message.from_user.id} card: {user[6]}</code>',
                f'3. Після переказу коштів введіть у чат боту суму відправлених коштів, що Ви надіслали',
                f'Увага, усі данні в кабінеті (номер карти, ваші гаманці) повинні бути валідними!',
                f'В іншому випадку адміністрація залишає за собою право відмовити у виплаті без жодних відшкодувань!',
                f'Якщо Ви НЕ отримали сповіщення про те, що заявка прийнята чи ні, надішліть її знову',
                f'Іноді є проблеми на стороні хостинга з інтернетом, тому іноді бот може не відповідати короткий термін часу',
            ]), reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id, f'Будь ласка, зазначте номер Вашої карти та Ваш Advcash акаунт у кабінеті',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def course(self, message):
        config = get_config()
        await self.bot.send_message(message.from_user.id,'\n'.join([
            f'Курс на {datetime.now().strftime("%d.%m.%Y")}',
            f'1 Payeer USD ➡️ {config["payeer_usd_to_uah"]} UAH',
            f'1 Advcash USD ➡️ {config["advcash_usd_to_uah"]} UAH',
        ]), reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def support(self, message):
        await self.bot.send_message(message.from_user.id,
                                    f'Контакти для отриманя підтримки:\n<code>@systnager</code> та <code>systnager@ukr.net</code>',
                                    reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def _register_new_user(self, message, user_id, ref_id):
        self.database.add_new_user(user_id)
        ref = self.database.get_user(ref_id) if ref_id else None
        if ref:
            ref = ref[0]
            if ref[4] == 'admin':
                self.database.change_user_refer(user_id, ref_id)
                await self.bot.send_message(int(ref_id), f'Вам приєднано вільного реферала з ID: {user_id} як адміну')
            else:
                self.database.change_user_refer(user_id, ref_id)
                await self.bot.send_message(int(ref_id), f'У Вас новий реферал з ID: {user_id}')
            return

        await self.bot.send_message(message.from_user.id, f'Вас НЕ приєднано до реферера')

    async def _make_exchange(self, message, user, withdraw_sum, config):
        if user:
            user = user[0]
            await self.bot.send_message(message.chat.id, 'Обмін успішно підтверджено',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))
            await self.bot.send_message(user[0], f'Ваша заявка на обмін {withdraw_sum}грн виконана')
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
            await self.bot.send_message(CHAT_ID, '\n'.join([
                f'Виплата за вивід з кабінету',
                f'id: <code>{message.chat.id}</code>',
                f'Username: <code>@{message.from_user.username}</code>',
                f'Номер карти: <code>{card_number}</code>',
                f'Сума для виплати: <code>{withdraw_money}</code>грн',
                f'Код для підтвердження виплати: <code>{user[0]} {withdraw_money}</code>',
            ]))
            await self.bot.send_message(message.from_user.id,
                                        f'Заявку прийнято. Виплата {withdraw_money}грн відбудеться протягом 48 годин❗️',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))
        else:
            await self.bot.send_message(message.from_user.id, f'Недостатня сума для виводу на балансі❗️',
                                        reply_markup=self.back_builder.as_markup(resize_keyboard=True))

    async def _command_start_handle(self, message):
        await self.bot.send_message(message.from_user.id,
                                    f'Привіт. Ми раді, що ти завітав до нас 🙂\nНаш чат: {CHAT_URL}')
        user_id = message.chat.id
        user = self.database.get_user(user_id)
        admins = self.database.get_admins()
        ref_id = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else random.choice(admins)[
            0] if admins else None

        if not user:
            await self._register_new_user(message, user_id, ref_id)

        await self.home(message)

    async def _on_button_click(self, message):
        user_id = message.from_user.id
        user = self.database.get_user(user_id)

        user_action = {
            'Головна': lambda: self.home(message),
            'Обмін': lambda: self.exchange(message),
            'Payeer USD\nКарта UAH': lambda: self.exchange_payeer_usd_to_uah(message),
            'Advcash USD\nКарта UAH': lambda: self.exchange_advcash_usd_to_uah(message),
            'Кабінет': lambda: self.cabinet(message),
            'Курс обміну': lambda: self.course(message),
            'Підтримка': lambda: self.support(message),
            'Вивести': lambda: self.withdraw(message),
            'Змінити Payeer акаунт': lambda: self.change_user_payeer_account(message),
            'Змінити Advcash акаунт': lambda: self.change_user_advcash_account(message),
            'Змінити номер банківської карти': lambda: self.change_user_card_number(message),
            'Інструкція по обміну': lambda: self.show_exchange_instruction(message),
            'Знайти реферала за айді': lambda: self.find_referral(message),

            'find_referral_state': lambda: self.find_referral_state(message),
            'exchange_payeer_usd_to_uah_state': lambda: self.exchange_payeer_usd_to_uah_state(message),
            'exchange_advcash_usd_to_uah_state': lambda: self.exchange_advcash_usd_to_uah_state(message),
            'change_user_payeer_account_state': lambda: self.change_user_payeer_account_state(message),
            'change_user_advcash_account_state': lambda: self.change_user_advcash_account_state(message),
            'change_user_card_number_state': lambda: self.change_user_card_number_state(message),
        }

        admin_action = {
            'Адмінка': lambda: self.bot.send_message(message.chat.id, 'Ви в адмінці',
                                                     reply_markup=self.admin_builder.as_markup(resize_keyboard=True)),
            'Сума для виплат рефоводам': lambda: self.show_sum_for_referral_withdraw(message),
            'Підтвердити виплату': lambda: self.set_confirm_withdraw_state(message),
            'Підтвердити обмін': lambda: self.set_confirm_exchange_state(message),
            'Змінити курс Payeer USD карта UAH': lambda: self.set_change_payeer_usd_to_uah_course_state(message),
            'Змінити курс Advcash USD карта UAH': lambda: self.set_change_advcash_usd_to_uah_course_state(message),
            'Змінити Advcash': lambda: self.set_change_advcash_account_state(message),
            'Змінити Payeer': lambda: self.set_change_payeer_account_state(message),
            'Відправити всім користувачам сповіщення': lambda: self.set_send_alert_for_all_users_state(message),
            'Відправити користувачу повідомлення': lambda: self.admin_send_alert_for_user_by_id(message),

            'withdraw': lambda: self.get_request_for_withdrawal(message),
            'confirm_withdraw': lambda: self.confirm_withdraw(message),
            'confirm_exchange': lambda: self.confirm_exchange(message),
            'change_payeer_usd_to_uah_course': lambda: self.change_payeer_usd_to_uah_course(message),
            'change_advcash_usd_to_uah_course': lambda: self.change_advcash_usd_to_uah_course(message),
            'change_payeer_account': lambda: self.change_bot_payeer_account(message),
            'change_advcash_account': lambda: self.change_bot_advcash_account(message),
            'send_alert_for_all_users': lambda: self.send_alert_for_all_users(message),
            'admin_send_alert_for_user_by_id': lambda: self.admin_send_alert_for_user_by_id_state(message),
        }

        if user:
            user = user[0]
            if message.text in user_action:
                await user_action[message.text]()
            elif user[1] in user_action:
                await user_action[user[1]]()
            elif user[4] == 'admin':
                user = self.database.get_user(user_id)
                user = user[0]
                if message.text in admin_action:
                    await admin_action[message.text]()
                elif user[1] in admin_action:
                    await admin_action[user[1]]()
        else:
            await self.bot.send_message(message.from_user.id, 'Потрібно пройти реєстрацію. Натисніть /start')
