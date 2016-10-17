import os
import db

from bs4 import BeautifulSoup


debug = False


def parse_comp_name(d):
	h = d.select("div.v-public-page-heading")
	if len(h):
		return h[0].text


def parse_competition(html_str, fname=""):

	# init html parser
	d = BeautifulSoup(html_str, 'html.parser')

	# competition id
	cid = os.path.basename(fname).split(".")[0]

	# create competition dict
	comp = {"id": cid, "name": parse_comp_name(d), "results": {}}
	if debug:
		print " * competition name: %s" % comp["name"]

	# for each class result table
	it1 = d.find_all("table")[1].find_all("table")[2:-1:2]
	it2 = d.find_all("table")[1].find_all("table")[3:-1:2]

	for ct, rt in zip(it1, it2):

		# parse class name
		k = ct.find_all("td")[1].text.strip()

		if not k:
			print " ** invalid class in file %s" % fname
			continue

		comp["results"][k] = []

		# parse results
		for result in rt.find_all("tr")[1:]:
			result_line = [ td.text.strip() for td in result.find_all("td") ]

			if len(result_line) < 5:
				print " ** invalid result in '%s': %s" % (fname, k)

			if result_line[0].isdigit():
				r = {
					"placing": result_line[0],
					"name": result_line[1],
					"club": result_line[2],
					"time": result_line[3],
					"diff": result_line[4]
				}
				comp["results"][k].append(r)

	return comp


def time_as_float(s):
	parts = map(float, s.split("."))

	if len(parts) == 3:
		h, m, s = parts
	elif len(parts) == 2:
		m, s = parts
		h = 0

	return 60.0 * h + m + s / 60.0


def persist_competition(conn, competition):

	assert "id" in competition
	assert "name" in competition
	assert "results" in competition

	# write competition row
	db.write_competition(conn, competition["id"], competition["name"])

	for klass, results in competition["results"].iteritems():
		for result in results:

			# find runner
			runner = db.read_runner_by_name(conn, result["name"])

			# create runner if not exists
			if not runner:
				runner = db.write_runner(conn, result["name"], result["club"])

			# write result record
			db.write_result(conn, runner["id"], competition["id"], klass,
							result["placing"], time_as_float(result["time"]),
							time_as_float(result["diff"]))

	conn.commit()


# database connection
conn = db.connect(db.conf)

# read directory listing
comp_dir = "competition_html"
fs = os.listdir(comp_dir)

# parse each file
for i, fn in enumerate(fs):
	fn = os.path.join(comp_dir, fn)
	competition = parse_competition(open(fn).read(), fn)
	persist_competition(conn, competition)
	print " * competition read: %d/%d" % (i+1, len(fs))

