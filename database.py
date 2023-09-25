import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('HOST'),
    user=os.getenv('USER'),
    password=os.getenv('PASSWORD'),
    database=os.getenv('DATABASE')
)

cursor = conn.cursor()


def write_new_item(table: str, columns: list, values: list):
    columns_clause = ', '.join([f"{col}" if isinstance(col, str) else str(col) for col in columns])
    values_clause = ', '.join([f"'{val}'" if isinstance(val, str) else str(val) for val in values])
    print(f"INSERT INTO user ('id', 'state', 'balance') VALUES (6517009257, 'default', 0);")

    print(f'INSERT INTO {table} ({columns_clause}) VALUES ({values_clause});')
    cursor.execute(f'INSERT INTO {table} ({columns_clause}) VALUES ({values_clause});')
    conn.commit()


def get_item(table, columns, params=None, param_values=None):
    if not (params is None or param_values is None):
        if len(params) != len(param_values) and columns != '*':
            raise ValueError("Number of columns and values should be the same")

    where_clause = " AND ".join(f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"
                                for col, val in zip(params, param_values)) if not (params is None or
                                                                                   param_values is None) else ''
    set_clause = "*" if columns == '*' else ", ".join(columns)
    where_clause = " WHERE " + where_clause if where_clause else ""
    print(f"SELECT {set_clause} FROM {table} {where_clause};")
    cursor.execute(f"SELECT {set_clause} FROM {table} {where_clause};")
    return cursor.fetchall()


def update_item(table, columns, values, params=None, param_values=None):
    if len(columns) != len(values) or len(params) != len(param_values):
        raise ValueError("Number of columns and values should be the same")

    set_clause = ", ".join(f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"
                           for col, val in zip(columns, values))

    where_clause = " AND ".join(f"{param} = '{param_val}'" if isinstance(param_val, str) else f"{param} = {param_val}"
                                for param, param_val in zip(params, param_values)
                                )

    where_clause = " WHERE " + where_clause if where_clause else ""
    print(f"UPDATE {table} SET {set_clause} {where_clause};")
    cursor.execute(f"UPDATE {table} SET {set_clause} {where_clause};")
    conn.commit()
