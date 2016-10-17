import urllib2
import os
import re
import random
import time

from bs4 import BeautifulSoup

host = "https://irma.suunnistusliitto.fi:8443"

# fetch cal
def fetch(url, host=""):
	data = urllib2.urlopen("%s%s" % (host, url)).read()
	print " * fetched %dk" % (len(data) / 1024)
	return data

def fetch_cal():
	cal_url = "/irma/public/competitioncalendar/view?year=2016&areaId=-1&discipline=SUUNNISTUS&competitionOpen=ALL"
	return fetch(cal_url, host)

def fetch_competition(url):
	return fetch(url, host)

def parse_cal(html_data):
	soup = BeautifulSoup(html_data, 'html.parser')
	return soup


def read_cal_cache(cal_file):
	if os.path.isfile(cal_file):
		return open(cal_file).read()

	data = fetch_cal()
	open(cal_file, "w").write(data)
	return data


def parse_result_urls(cal):
	copmetition_urls = []

	for a in cal.find_all(name="a"):
		s = a.attrs["href"]

		if s.startswith("/irma/public/competition/results"):
			a = s.find("?id=")
			if a < 0:
				continue
			copmetition_urls.append(s)

	return copmetition_urls

def parse_competition_id(url):
	a = url.find("?id=")
	if a < 0:
		raise Exception, "no competition id in url"
	return url[a+4:]


def sleep_jitter(t=1.0):
	t += t / 2.0 * (random.random() - 0.5)
	time.sleep(t)


comp_dir ="competition_html"

def get_status_file_name():
	return os.path.join(comp_dir, "done.txt")


def write_status(s):
	with open(get_status_file_name(), "a") as fp_done:
		fp_done.write("%s\n" % s)


def read_status():
	fn = get_status_file_name()

	if not os.path.isfile(fn):
		return []

	return [ l.strip() for l in open(fn).readlines() ]


def fetch_competitions(urls):

	# create dir
	if not os.path.isdir(comp_dir):
		os.mkdir(comp_dir)

	# read status
	dones = read_status()

	for url in urls:
		if url in dones:
			print " * already done: %s" % url
			continue

		cid = parse_competition_id(url)
		comp_data = fetch_competition(url)

		# write to file
		html_file = "%s.html" % cid
		fn = os.path.join(comp_dir, html_file)
		open(fn, "w").write(comp_data)

		write_status(url)
		sleep_jitter()


# read calendar
cal_file = "cal/cal.html"
data = read_cal_cache(cal_file)
cal = parse_cal(data)

# parse result urls
copmetition_urls = parse_result_urls(cal)
print " * competitions found: %d" % len(copmetition_urls)

# fetch competition htmls
fetch_competitions(copmetition_urls)
