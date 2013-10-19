drop table if exists posts;
create table posts (
	id integer primary key autoincrement,
	evaluation integer,
	ip_address text,
	original_text text,
	readability float,
	grade integer,
	timedate text,
	avg_num_of_words integer,
	kango float,
	wago float,
	doushi float,
	joshi float
);