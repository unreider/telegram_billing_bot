import os
import sqlite3

from typing import List, Tuple

conn = sqlite3.connect("billing.db")
cursor = conn.cursor()


def insert(table: str, column_values: dict):
	columns = ', '.join(column_values.keys())
	values = [tuple(column_values.values())]
	placeholders = ", ".join( "?" * len(column_values.keys()) )
	cursor.executemany(
		f"INSERT INTO {table}"
		f"({columns})"
		f"VALUES ({placeholders})",
		values)
	conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Tuple]:
	print('columns', columns)
	columns_joined = ", ".join(columns)
	print('columns_joined', columns_joined)
	cursor.execute(f"SELECT {columns_joined} FROM {table}")
	rows = cursor.fetchall()
	print('rows', rows)
	result = []
	for row in rows:
		dict_row = {}
		for index, column in enumerate(columns):
			dict_row[column] = row[index]
		result.append(dict_row)
	print('result', result)
	# return result


def delete(table: str, record_id: int) -> None:
	cursor.execute(f"DELETE FROM {table} WHERE id={record_id}")
	conn.commit()


# Get category's id if name given, or name if id given. By changing to parameter
def get_category_param(param1: str, param2: str, category_param) -> int:
	category_param = str(category_param) # in case it's id - int
	param1 = str(param1) # in case it's id - int
	param2 = str(param2) # in case it's id - int
	# There was a problem, I forgot to add '' to category_param
	cursor.execute(f"SELECT {param1} FROM category WHERE {param2} = '{category_param}'")
	# Fetch the category Parameter
	category_parameter = cursor.fetchone()
	return category_parameter[0]


def get_cursor():
	return cursor


def _init_db():
	with open("createdb.sql", "r") as f:
		sql = f.read()
	cursor.executescript(sql)
	conn.commit()


def check_db_exists():
	cursor.execute("""SELECT name FROM sqlite_master 
					WHERE type='table' AND name='expense'
					AND name='budget'""")
	table_exists = cursor.fetchall()
	if table_exists:
		return
	_init_db()

check_db_exists()
