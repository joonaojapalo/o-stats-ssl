import sys
import math
from collections import defaultdict

import db

sql = """
select
	c.name,
	re.class,
	ru.name,
	ru.club,
	re.placing,
	re.time,
	re.diff_time,
	re.diff_time / re.time
from results as re
join
	runners as ru on ru.id = re.runner_id
join
	competitions as c on c.id = re.competition_id
where
	re.class LIKE "%s" OR
	re.class LIKE "%sA"
"""

def mean(l):
	N = len(l) + 1
	return sum(l) / N if N else 0


def var(l):
	N = len(l) + 1
	m = mean(l)
	return sum([(x - m)**2 for x in l])/N


def std(l):
	return math.sqrt(var(l))


if __name__ == "__main__":

	if len(sys.argv) < 2:
		print " ** class missing"
		print
		sys.exit(1)

	conn = db.connect(db.conf)
	klass = sys.argv[1]

	rows = defaultdict(lambda:{"r": []})

	for r in conn.execute(sql % (klass, klass)):
		name = r[2]
		rows[name]["r"].append(r[7])

	# compute stats
	rank = []
	for name, data in rows.iteritems():
		n_comp = len(data["r"])

		# threshold
		if n_comp > 2:
			d = data["r"]
			sortable = mean(d)
			rank.append((name, d, sortable))

	# order & plot
	rank.sort(lambda a,b:cmp(a[2], b[2]))
	s = "\n".join(("%3.i. %s\t\t%.3f, avg=%.3f std=%.3f, min=%.3f, max=%.3f (%d)" % (n+1, r[0], r[2], mean(r[1]), std(r[1]), min(r[1]), max(r[1]), len(r[1])) for (n, r) in enumerate(rank)))
	print s.encode("utf-8")

