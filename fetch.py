import urllib2
import os
import re
import random
import time
import sys
import re

from bs4 import BeautifulSoup

import config
from fsutils import FileRepository


# uri builder
def get_cal_uri(year, discipline="SUUNNISTUS"):
	return "/irma/public/competitioncalendar/view?year=%i&areaId=-1&discipline=%s&competitionOpen=ALL" % (year, discipline)

# fetch cal
def fetch(url, host):
	data = urllib2.urlopen("%s%s" % (host, url)).read()
	print " * fetched %dk" % (len(data) / 1024)
	return data

def fetch_cal(year, host):
	cal_url = get_cal_uri(year)
	return fetch(cal_url, host)

def fetch_competition(url, host):
	return fetch(url, host)

def parse_cal(html_data):
	soup = BeautifulSoup(html_data, 'html.parser')
	return soup


def read_cal_cache(cal_file, host, year):
	if os.path.isfile(cal_file):
		return open(cal_file).read()

	data = fetch_cal(year, host)
	open(cal_file, "w").write(data)
	return data


def parse_result_urls(cal_soup):
	competition_urls = []

	for a in cal_soup.find_all(name="a"):
		if "href" not in a.attrs:
			continue

		s = a.attrs["href"]

		if s.startswith("/irma/public/competition/results"):
			a = s.find("?id=")
			if a < 0:
				continue
			competition_urls.append(s)

	return competition_urls


def parse_competition_id(url):
	match = re.search(r"\?id=([0-9]+)&?", url)

	if not match:
		raise Exception, "no competition id in url"

	return match.groups(1)


def sleep_jitter(t=1.0):
	t += t / 2.0 * (random.random() - 0.5)
	time.sleep(t)


comp_dir ="competition_html"

#def get_status_file_name():
#	return os.path.join(comp_dir, "done.txt")


def write_status(fsrepo, fname):
	with open(fsrepo.get_fetched_htmls_journal_file_path(), "a") as fp_done:
		fp_done.write("%s\n" % fname)


def read_status(fsrepo):
	fn = fsrepo.get_fetched_htmls_journal_file_path() #get_status_file_name()

	if not os.path.isfile(fn):
		return []

	return [ l.strip() for l in open(fn).readlines() ]


def fetch_competitions(fsrepo, host, urls):

	# create dir
	#if not os.path.isdir(comp_dir):
	#	os.mkdir(comp_dir)

	# read status
	dones = read_status(fsrepo)

	for url in urls:
		if url in dones:
			print " * already done: %s" % url
			continue

		cid = parse_competition_id(url)
		comp_data = fetch_competition(url, host)

		# write to file
		html_file = "%s.html" % cid
		fn = os.path.join(fsrepo.get_html_base(), html_file)
		open(fn, "w").write(comp_data)

		write_status(fsrepo, url)
		sleep_jitter()


if __name__ == "__main__":

	# parse args
	if len(sys.argv) < 2:
		print "Missing year."
		sys.exit(1)

	year = int(sys.argv[1])

	print " * start fetching year: %i" % (year,)

	# init file repo
	fsrepo = FileRepository(config.conf["rootpath"], str(year))
	fsrepo.ensure_directory_layout()

	# read calendar
	calfile = fsrepo.get_calendar_html_path() # "cal/cal.html"
	data = read_cal_cache(calfile, config.conf["host"], year)
	cal_soup = parse_cal(data)
	print " * calendar parsed: %s" % year

	# parse result urls
	competition_urls = parse_result_urls(cal_soup)
	print " * competitions found: %d" % len(competition_urls)

	# fetch competition htmls
	fetch_competitions(fsrepo, config.conf["host"], competition_urls)
