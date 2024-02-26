# Billing Bot - t.me/mybilling0_bot
import os
import asyncio
import logging
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
# from aiogram import F
# from aiogram.utils.keyboard import InlineKeyboardBuilder

import expenses

# TELEGRAM_API_TOKEN
API_TOKEN = "6523232569:AAE6ge9q69NaltP2HWZXwTYLqy_HnHgJ7V4"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
	answer_message = "Welcome to my Billing Bot!\n" + \
	"List of all commands:\n" + \
	"/listexpenses - get the list of your expenses\n" + \
	"/addexpense <name> <amount> <category> - add a new expense on your list\n" + \
	"/listbudgets - get your last 10 budget records\n" + \
	"/budgetnow - get your current budget info\n" + \
	"/addbudget <name> <amount> <currency(usd/rub/amd)> " + \
		"- change your current budget\n" + \
	"/listcategories - get your last 10 categories\n" + \
	"/addcategory <name> <description> - add a new category"
	await message.answer(answer_message)


@dp.message(Command("listexpenses"))
async def list_expenses(message: types.Message):
	last_expenses = expenses.last_expenses()
	last_expenses_rows = [
		f"{exp.currency}{exp.amount} on {exp.name} - {exp.category_name} - click "
		f"/delexpense{exp.id} to delete"
		for exp in last_expenses]
	answer_message = "List of last 10 expenses: \n\n* " + "\n\n* "\
		.join(last_expenses_rows)
	await message.answer(answer_message)


# /add <name> <amount> <category>
@dp.message(lambda message: message.text.startswith('/addexpense'))
async def add_expense(message: types.Message):
	if message.text == '/addexpense' or \
	not bool(re.search(r'\d', message.text)):
		answer_message = "Wrong Parameters!\n" + \
		"Right usage: /addexpense <name> <amount>\n" + \
		"See /start"
		await message.answer(answer_message)
	else:
		raw_message = message.text.replace('/addexpense ', '')
		expense_message = expenses.add_expense(raw_message)
		if expense_message.category_id == None:
			answer_message = f"""There is no category with the name
				{expense_message.category_name}\nThe command for adding a new 
				category - /add_category <name> <description>"""
			await message.answer()
		else:
			await message.answer("Added " + raw_message)


@dp.message(lambda message: message.text.startswith('/delexpense'))
async def del_expense(message: types.Message):
	expense_id = int(message.text.replace('/delexpense', ''))
	expenses.delete_record('expense', expense_id)
	await message.answer("Deleted.")


@dp.message(Command('listbudgets'))
async def last_budget(message: types.Message):
	# get last 10 Budget records
	if message.text != '/listbudgets':
		await message.answer("Wrong parameters!")
	else:
		budget_message = expenses.last_budget()
		last_budget_rows = [
			f"{budg.currency}{budg.amount} - '{budg.name}' - click "
			f"/delbudget{budg.id} to delete"
			for budg in budget_message]
		answer_message = "List of last 10 budget records: \n\n* " + "\n\n* "\
		.join(last_budget_rows)
		await message.answer(answer_message)


@dp.message(Command('budgetnow'))
async def budget_now(message: types.Message):
	if not message.text == '/budgetnow':
		await message.answer('Wrong parameters!')
	else:
		budget_message = expenses.budget_now()
		budget = budget_message[0]
		remaining = budget_message[1]
		answer_message = "Your budget: " + \
		f"{budget.currency}{budget.amount} " + \
		f"- '{budget.name}'\n" + f"Remaining budget: {budget.currency}{remaining}"
		await message.answer(answer_message)


# $, ₽, ֏
# /add_budget name amount currency(usd/rub/amd)
@dp.message(lambda message: message.text.startswith('/addbudget'))
async def add_budget(message: types.Message):
	currencies = ['usd', 'rub', 'amd']
	currency_exists = [True for c in currencies if c in message.text]
	if message.text == '/addbudget' or \
	not bool(re.search(r'\d', message.text)) or \
	not currency_exists or \
	len(message.text.split()) < 3:
		# re.search to check if there is 1 or more digits
		answer_message = "Wrong parameters!\n" + \
		"Right usage: /addbudget <name> <amount> " + \
		"<currency(usd/rub/amd)>\n" + \
		"See /start"
		await message.answer(answer_message)
	else:
		raw_message = message.text.replace('/addbudget ', '')
		budget_message = expenses.change_budget(raw_message)
		await message.answer("Budget now is " + raw_message)


@dp.message(lambda message: message.text.startswith('/delbudget'))
async def del_budget(message: types.Message):
	budget_id = int(message.text.replace('/delbudget', ''))
	expenses.delete_record('budget', budget_id)
	await message.answer("Deleted.")


@dp.message(Command('listcategories'))
async def last_category(message: types.Message):
	# get last 10 Categories
	if message.text != "/listcategories":
		await message.answer("Wrong Parameters!")
	else:
		category_message = expenses.last_category()
		last_category_rows = [
			f"{cat.name}" + (f" - {cat.description}" if \
			cat.description != '' else '') + \
			f" - click /delcategory{cat.id} to delete"
			for cat in category_message]
		answer_message = "List of last 10 categories: \n\n* " + "\n\n* "\
		.join(last_category_rows)
		await message.answer(answer_message)


# /add_category <name> <description>
@dp.message(lambda message: message.text.startswith('/addcategory'))
async def add_category(message: types.Message):
	# < 2 is with '/addcategory'
	if message.text == '/addcategory' or \
	len(message.text.split()) < 2:
		answer_message = "Wrong parameters!\n" + \
		"Right usage: /addcategory <name> <description>\n" + \
		"See /start"
		await message.answer(answer_message)
	else:
		raw_message = message.text.replace('/addcategory', '')
		category_message = expenses.add_category(raw_message)
		if category_message.description != '':
			answer_message = f"Added a new category: {category_message.name}" + \
				f" - {category_message.description}"
		else:
			answer_message = f"Added a new category: {category_message.name}"
		await message.answer(answer_message)


@dp.message(lambda message: message.text.startswith('/delcategory'))
async def del_category(message: types.Message):
	category_id = int(message.text.replace('/delcategory', ''))
	expenses.delete_record('category', category_id)
	await message.answer("Deleted.")


async def main():
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
