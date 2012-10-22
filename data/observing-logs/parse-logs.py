"""This script runs through INT log files, parses them, 
and summarizes their contents into CSV tables for analysis"""

import re
import numpy as np
import os

csv_bynight = open("logs_bynight.csv", "w")
csv_byrun = open("logs_byrun.csv", "w")

# CSV headers
csv_bynight.write("night,observer,temp_avg,hum_avg,lost_weather,lost_technical,lost_other,comments_weather,comments_night\n")
csv_byrun.write("run,name,ra,dec,night,observer,temp_avg,hum_avg,lost_weather,lost_technical,lost_other,comments_weather,comments_night,comments_exposure\n")


for filename in sorted(os.listdir("downloaded")):
	if not re.match("intlog_\d+.txt", filename):
		continue

	f = open("downloaded/"+filename, "r")
	log = f.readlines()


	temp, hum = [], []

	# Assume headers take no more than 70 lines
	for i, line in enumerate(log[0:70]):
		m = re.match("^DATE\s*(\d+)", line, re.M|re.S)
		if m: night = m.group(1)

		m = re.match("^OBSERVER/S\s*(.*)\s+$", line, re.M|re.S)
		if m: observer = m.group(1).replace('"', '""')

		m = re.match("^\d{2}:00\s+([0-9.]+)\s+([0-9.]+)", line, re.M|re.S)
		if m: 
			temp.append( m.group(1) )
			hum.append( m.group(2) )

		m = re.match("^TIME LOST weather\s+(\d+:\d+)", line, re.M|re.S)
		if m: lost_weather = m.group(1)

		m = re.match("^TIME LOST Technical\s+(\d+:\d+)", line, re.M|re.S)
		if m: lost_technical = m.group(1)

		m = re.match("^TIME LOST Other\s+(\d+:\d+)", line, re.M|re.S)
		if m: lost_other = m.group(1)

		m = re.match("^WEATHER CONDITIONS(.*)", line, re.M|re.S)
		if m: weather = log[i+1].strip().replace('"', '""')

		m = re.match("^COMMENTS(.*)", line, re.M|re.S)
		if m: night_comments = log[i+1].strip().replace('"', '""')



	out = "%s,\"%s\",%.1f,%.1f,%s,%s,%s,\"%s\",\"%s\"\n" % \
			(night, observer, \
			np.mean(np.array(temp, dtype="float")), \
			np.mean(np.array(hum, dtype="float")), \
			lost_weather, lost_technical, lost_other,
			weather, night_comments)
	csv_bynight.write(out)


	# Data
	for line in log[20:]:

		m = re.match("^\s+(\d+).*WFC", line, re.M|re.S)
		if m:
			run = m.group(1).strip()
			name = line[8:25].strip()
			ra = line[25:36].strip()
			dec = line[37:48].strip()
			comments = line[121:].strip().replace('"', '""')


			out = "%s,\"%s\",%s,%s,%s,\"%s\",%.1f,%.1f,%s,%s,%s,\"%s\",\"%s\",\"%s\"\n" % \
					(run, name, ra, dec, \
					night, observer, \
					np.mean(np.array(temp, dtype="float")), \
					np.mean(np.array(hum, dtype="float")), \
					lost_weather, lost_technical, lost_other,
					weather, night_comments, comments)
			csv_byrun.write(out)

	csv_bynight.flush()
	csv_byrun.flush()


csv_bynight.close()
csv_byrun.close()