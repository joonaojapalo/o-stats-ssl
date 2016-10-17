CREATE TABLE runners (
	id INTEGER PRIMARY KEY,
	name VARCHAR,
	club VARCHAR
);

CREATE TABLE competitions (
	id INTEGER PRIMARY KEY,
	name VARCHAR
);

CREATE TABLE results (
	id INTEGER PRIMARY KEY,
	competition_id INT,
	runner_id INT,
	class VARCHAR,
	placing INT,
	time REAL,
	diff_time REAL,
	FOREIGN KEY (competition_id) REFERENCES competitions(id),
	FOREIGN KEY (runner_id) REFERENCES runners(id)
);
