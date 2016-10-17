import sqlite3


conf = {
	"sqlite": "competitions-2016.db3"
}


def create_schema(conn):
	schema = open("schema.sql").read()
	for ddl_statement in schema.split(";"):
		conn.execute(ddl_statement) 


def connect(conf):
	return sqlite3.connect(conf["sqlite"])


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


if __name__ == "__main__":
	print " * creating schema"
	conn = connect(conf)
	create_schema(conn)
