"""Parse the outputs of 'get_seeing.perl'
and summarizes the contents into a CSV table"""

import re
import numpy as np
import os

csv_seeing = open("seeing.csv", "w")

# CSV headers
csv_seeing.write("night,run,field,filter,seeing,ellipt,sky,sources\n")

mydir = "fall2012/"

for filename in sorted(os.listdir(mydir)):
	if not re.match("seeing_\d+.log", filename):
		continue

	night = filename[7:15]

	f = open(mydir+filename, "r")

	# Data
	for line in f.readlines():
		fields = re.split('\s+', line)
		if len(fields) > 7 and fields[7] == 'sources':
			# which gives you file number, FWHM in pixel, FWHM in arcsec, 
			# ellipticity, sky background
			run = fields[0].split('.')[0]
			seeing = fields[2]
			ellipt = fields[3]
			sky = fields[4]
			sources = fields[6]
			field = fields[9]
			filt = fields[10]

			out = "%s,%s,%s,%s,%s,%s,%s,%s\n" % \
				(night, run, field, filt, seeing, ellipt, sky, sources)
			csv_seeing.write(out)


csv_seeing.close()