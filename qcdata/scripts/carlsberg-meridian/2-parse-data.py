"""
This script converts extinction and photometricity data from the 
Carlsberg Meridian Telescope into a single CSV table
"""

csv = open("carlsberg.csv", "w")
csv.write("night,ext_r,f_phot\n")

f = open("data/camcext.concatenated", "r")
for line in f.readlines():
	# Fraction of hours which were photometric
	try:
		hours_phot = float(line[56:61])
		hours_nonphot = float(line[62:67])
		# Fraction of hours which where photometric
		fraction = round(hours_phot / (hours_phot + hours_nonphot),2)
		csv.write("%s,%s,%s\n" % (line[16:22], line[29:35].strip(), fraction))
	except ZeroDivisionError:
		csv.write("%s,,\n" % (line[16:22]))

csv.close()
