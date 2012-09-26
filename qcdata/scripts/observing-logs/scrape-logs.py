"""
Script to download INT observing logs
for the purpose of analyzing IPHAS survey observer comments

Copyright, the authors 2012.
"""
import mechanize
import datetime
import time


def get_int_log(year, month, day):
	br = mechanize.Browser()
	br.open("http://www.ing.iac.es/astronomy/observing/inglogs.php")
	br.select_form(nr=1)
	br["form[tel]"] = ["int"]
	br["form[day]"] = ["%02i" % day]
	br["form[month]"] = ["%02i" % month]
	br["form[year]"] = ["%s" % year]
	response = br.submit(nr=1)
	return response.get_data()


date = datetime.datetime(2006, 2, 24)
now = datetime.datetime.now()
while date < now:
	print "Now requesting %s" % date
	log = get_int_log(date.year, date.month, date.day)
	# Write to file
	f = open("downloaded/intlog_%04i%02i%02i.txt" \
						% (date.year, date.month, date.day), "w")
	f.write(log)
	f.close()
	# Continue on!
	date += datetime.timedelta(days=1)
	time.sleep(1)