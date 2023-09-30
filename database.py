import os
import mysql.connector
from dotenv import load_dotenv

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

    def write_new_item(self, table: str, columns_params: dict):
        columns_clause = ', '.join([f"{col}" if isinstance(col, str) else str(col) for col in columns_params.keys()])
        values_clause = ', '.join([f"'{val}'" if isinstance(val, str) else str(val) for val in columns_params.values()])
        request = f'INSERT INTO {table} ({columns_clause}) VALUES ({values_clause});'
        print(request)
        self.cursor.execute(request)
        self.conn.commit()

    def get_item(self, table, columns='*', filter_params=None):
        if filter_params is None:
            filter_params = {}
        print(filter_params, columns, table)

        where_clause = " AND ".join(f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"
                                    for col, val in zip(filter_params.keys(), filter_params.values())) if not (filter_params is None) else ''
        set_clause = "*" if columns == '*' else ", ".join(columns)
        where_clause = " WHERE " + where_clause if where_clause else ""
        request = f"SELECT {set_clause} FROM {table} {where_clause};"
        print(request)
        self.cursor.execute(request)
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
        print(request)
        self.cursor.execute(request)
        self.conn.commit()
