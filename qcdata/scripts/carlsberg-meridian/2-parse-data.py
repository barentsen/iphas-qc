"""
This script converts extinction and photometricity data from the 
Carlsberg Meridian Telescope into a single CSV table
"""

csv = open("carlsberg.csv", "w")
csv.write("night,ext_r,hours_phot,hours_nonphot\n")

f = open("data/camcext.concatenated", "r")
for line in f.readlines():
	hours_phot = float(line[56:61])
	hours_nonphot = float(line[62:67])
	csv.write("20%06d,%s,%s,%s\n" % \
		(int(line[16:22]), line[29:35].strip(), hours_phot, hours_nonphot))

csv.close()
