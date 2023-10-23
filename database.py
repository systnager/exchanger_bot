import os
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import OperationalError

load_dotenv()


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv('HOST'),
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD'),
            database=os.getenv('DATABASE')
        )

        self.cursor = self.conn.cursor()

    def connect_to_database(self):
        self.cursor = self.conn.cursor()

    def complete_sql_request(self, request):
        while True:
            try:
                self.cursor.execute(request)
                break
            except OperationalError:
                self.connect_to_database()

    def write_new_item(self, table: str, columns_params: dict):
        columns_clause = ', '.join([f"{col}" if isinstance(col, str) else str(col) for col in columns_params.keys()])
        values_clause = ', '.join([f"'{val}'" if isinstance(val, str) else str(val) for val in columns_params.values()])
        request = f'INSERT INTO {table} ({columns_clause}) VALUES ({values_clause});'
        self.complete_sql_request(request)
        self.conn.commit()

    def get_item(self, table, columns='*', filter_params=None):
        if filter_params is None:
            filter_params = {}

        where_clause = " AND ".join(f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"
                                    for col, val in zip(filter_params.keys(), filter_params.values())) if not (filter_params is None) else ''
        set_clause = "*" if columns == '*' else ", ".join(columns)
        where_clause = " WHERE " + where_clause if where_clause else ""
        request = f"SELECT {set_clause} FROM {table} {where_clause};"
        self.complete_sql_request(request)
        return self.cursor.fetchall()

    def update_item(self, table, columns_params=None, filter_params=None):
        if columns_params is None:
            columns_params = {}
        if filter_params is None:
            filter_params = {}

        set_clause = ", ".join(f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"
                               for col, val in zip(columns_params.keys(), columns_params.values()))

        where_clause = " AND ".join(f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"
                                    for col, val in zip(filter_params.keys(), filter_params.values())) if not (filter_params is None) else ''

        where_clause = " WHERE " + where_clause if where_clause else ""
        request = f"UPDATE {table} SET {set_clause} {where_clause};"
        self.complete_sql_request(request)
        self.conn.commit()

    def get_user(self, user_id: int):
        return self.get_item('user', '*', {'id': user_id})

    def get_users(self):
        return self.get_item('user', '*')

    def get_admins(self):
        return self.get_item('user', '*', {'id': 'admin'})

    def add_new_user(self, user_id, state='default', balance=0, invited_by=None):
        user_info = {
            'id': user_id,
            'state': state,
            'balance': balance,
            'role': 'user',
        }

        if invited_by:
            user_info['invited_by'] = invited_by
        self.write_new_item('user', user_info)

    def change_user_refer(self, user_id, refer_id):
        self.update_item('user', {'invited_by': refer_id}, {'id': user_id})

    def change_user_balance(self, user_id, balance):
        self.update_item('user', {'balance': balance}, {'id': user_id})

    def changer_user_state(self, user_id: int, state: str):
        self.update_item('user', {'state': state}, {'id': user_id})

    def changer_user_payeer_account(self, user_id: int, payeer_account: str):
        self.update_item('user', {'payeer_account': payeer_account}, {'id': user_id})

    def changer_user_card_number(self, user_id: int, card_number: int):
        self.update_item('user', {'card_number': card_number}, {'id': user_id})

    def get_user_referrals_count(self, user_id: int) -> int:
        return len(self.get_item('user', filter_params={'invited_by': user_id}))
