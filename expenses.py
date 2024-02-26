# Expenses handling
import re
import db
import datetime
import pytz

from typing import List, NamedTuple, Optional


class Message(NamedTuple):
	name: str
	amount: int


class Expense(NamedTuple):
	id: Optional[int]
	name: str
	amount: int
	currency: str
	category_id: int
	category_name: str


class Budget(NamedTuple):
	id: Optional[int]
	name: str
	amount: int
	currency: str  # char


class Category(NamedTuple):
	id: Optional[int]
	name: str
	description: str


def add_expense(raw_message: str) -> Expense:
	# parsed_message = _parse_message(raw_message)
	raw_message_list = raw_message.split()
	# Not effective approach
	name = raw_message_list[0]
	amount = raw_message_list[1]
	category_name = raw_message_list[2]
	currency = _get_currency()
	if _check_category_exists('name', category_name):
		category_id = db.get_category_param('id', 'name', category_name)
	else:
		category_id = None
		return Expense(id=None,
			name=name,
			amount=amount,
			currency=currency,
			category_id=category_id,
			category_name=category_name)
	db.insert("expense", {
		"name": name,
		"amount": amount,
		"created": _get_now_formatted(),
		"category_id": category_id,
		"raw_text": raw_message
	})
	return Expense(
		id=None,
		name=name,
		amount=amount,
		currency=currency,
		category_id=category_id,
		category_name=None)


def last_expenses() -> List[Expense]:
	cursor = db.get_cursor()
	cursor.execute(
		"SELECT * FROM expense "
		"order by created desc limit 10"
	)
	rows = cursor.fetchall()
	currency = _get_currency()
	if len(rows) > 0:
		last_expenses_by_rows = [
			Expense(id=row[0], name=row[1], amount=row[2], currency=currency, \
			category_id=None, category_name=db.get_category_param('name', 'id', row[4])) for row in rows]
	else: last_expenses_by_rows = []
	return last_expenses_by_rows


def delete_record(table: str, record_id: int) -> None:
	db.delete(table, record_id)


def last_budget() -> Budget:
	# get last 10 Budget records
	cursor = db.get_cursor()
	cursor.execute(
		"SELECT * FROM budget "
		"ORDER BY id DESC LIMIT 10")
	rows = cursor.fetchall()
	budget_by_rows = [Budget(
		id=row[0], name=row[1], amount=row[2],
		currency=_change_currency(row[3])) for row in rows]
	return budget_by_rows


def change_budget(raw_message: int) -> Budget:
	raw_message_list = raw_message.split()
	# not effective
	name = raw_message_list[0]
	amount = raw_message_list[1]
	currency = raw_message_list[2]
	db.insert("budget", {
		"name": name,
		"amount": amount,
		"currency": currency,
		"raw_text": raw_message
	})
	return Budget(
		id=None,
		name=name,
		amount=amount,
		currency=currency)


def budget_now() -> Budget:
	cursor = db.get_cursor()
	cursor.execute("SELECT * FROM budget ORDER BY ID DESC LIMIT 1")
	last_budget = cursor.fetchone()
	budget_id = last_budget[0]
	budget_name = last_budget[1]
	budget_amount = last_budget[2]
	budget_currency = _change_currency(last_budget[3])

	budget = Budget(
		id=budget_id,
		name=budget_name,
		amount=budget_amount,
		currency=budget_currency)

	expenses = last_expenses()
	amount = [exp.amount for exp in expenses]
	sum = 0
	for i in amount: sum += i
	remaining = budget_amount - sum

	return [budget, remaining]


def last_category() -> List[Category]:
	cursor = db.get_cursor()
	cursor.execute(
		"SELECT * FROM category "
		"ORDER BY id DESC LIMIT 10")
	rows = cursor.fetchall()
	category_by_rows = [Category(
		id=row[0], name=row[1], description=(row[2] if row[2] != '' else ''))
		for row in rows]
	return category_by_rows


def add_category(raw_message: str) -> Category:
	raw_message_list = raw_message.split()
	name = raw_message_list[0]
	description = ' '.join(raw_message_list[1:]) # from 2nd element to the end
	db.insert("category", {
		"name": name,
		"description": description
	})
	return Category(
		id=None,
		name=name,
		description=description)


def _get_currency():
	cursor = db.get_cursor()
	cursor.execute(
		"SELECT currency FROM budget "
		"ORDER BY ID DESC LIMIT 1"
	)
	budget = cursor.fetchone()
	if budget:
		currency = budget[0]
	else: currency = None
	changed_currency = _change_currency(currency)
	return changed_currency


def _change_currency(currency: str):
	if currency == 'usd': changed_currency = '$'
	elif currency == 'rub': changed_currency = '₽'
	elif currency == 'amd': changed_currency = '֏'
	else: changed_currency = None
	return changed_currency


def _check_category_exists(param: str, category_param: str):
	cursor = db.get_cursor()
	cursor.execute(f"SELECT * FROM category WHERE {param} = '{category_param}'")
	rows = cursor.fetchall()
	if len(rows) > 0:
		return True
	else:
		return False


# def _parse_message(raw_message: str) -> Message:
# 	amount = int(re.search(r'\d+', raw_message).group())
# 	name = raw_message.replace(str(amount), '')
# 	return Message(name=name, amount=amount)


def _get_now_formatted() -> str:
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    tz = pytz.timezone("Asia/Yerevan")
    now = datetime.datetime.now(tz)
    return now