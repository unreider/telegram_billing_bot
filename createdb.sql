create table if not exists category(
	id integer primary key,
	name text,
	description text
);

create table if not exists expense(
	id integer primary key,
	name text,
	amount integer,
	created datetime,
	category_id integer,
	raw_text text,
	FOREIGN KEY(category_id) REFERENCES category(id)
);

create table if not exists budget(
	id integer primary key, -- A unique identifier for each budget record
	name text, -- helps users identify and manage different budgets
	amount integer, -- helps users identify and manage different budgets
	currency text,
	raw_text text
);