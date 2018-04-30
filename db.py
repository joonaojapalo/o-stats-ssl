import sqlite3


def build_conf():
	return {
		"type": "sqlite",
		"connection": ""
	}


def create_schema(conn):
	schema = open("persistence/schema.sql").read()
	for ddl_statement in schema.split(";"):
		conn.execute(ddl_statement) 


def connect(conf):
	if conf["type"] == "sqlite":
		return sqlite3.connect(conf["connection"])
	else:
		raise Exception("invalid database tyype: %s" % conf["type"])


def write_runner(conn, runner):
	pass


def write_competition(conn, id, name):
	conn.execute("INSERT INTO competitions (id, name) VALUES (?, ?)", (id, name))


def write_result(conn, runner_id, competition_id, klass, placing, time, diff_time):
	result = (
		int(competition_id),
		int(runner_id),
		klass,
		int(placing), float(time), float(diff_time)
		)
	conn.execute("INSERT INTO results (competition_id, runner_id, class, placing, time, diff_time) VALUES (?, ?, ?, ?, ?, ?)", result)


def write_runner(conn, name, club):
	"""
		Returns runner id
	"""
	conn.execute("INSERT INTO runners (name, club) VALUES (?, ?)", (name, club))
	rid = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
	return {"id": rid, "name": name, "club": club}


def read_runner_by_name(conn, name):
	r = conn.execute("SELECT id, name, club FROM runners WHERE name = ?", (name,)).fetchone()

	if not r:
		return

	return {"id": int(r[0]), "name": r[1], "club": r[2]}


def create_sqlite_by_filename(fname):
	conf = build_conf()
	conf["connection"] = fname
	conn = connect(conf)

	print " * creating schema"
	create_schema(conn)
	
	return conn

