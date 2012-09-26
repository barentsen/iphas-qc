"""
This script assigns re-observation priorities to IPHAS fields.

1: Missing fields (no observation available at all)
2: Horrible fields (no observation with seeing < 2 & ellipt < 0.2)
3: Suspect fields - fields left out of FINALSOL3.TXT
"""

import pyfits





d = pyfits.getdata("../qcdata/scripts/iphas-fields-observed.fits", 1)

csv_missing = open("1-the-missing.txt", "w")
csv_horrible = open("2-the-horrible.txt", "w")
csv_suspect = open("3-the-suspect.txt", "w")

for i in range(1, 7636):
	fieldname = "%04d" % i
	for field in [fieldname, fieldname+"o"]:
		c = d['field'] == field
		
		# Check for zero observations
		if c.sum() == 0:
			csv_missing.write("%s\n" % field)
			continue
		
		# Check for poor quality
		c_good = (d['seeing'][c] < 2) & (d['ellipt'][c] < 0.2)
		if c_good.sum() == 0:
			csv_horrible.write("%s\n" % field)
			continue
		
		# Check for suspect
		c_suspect = d['anchor'][c] > -99
		if c_suspect.sum() == 0:
			csv_suspect.write("%s\n" % field)
			


# Close files
for f in [csv_missing, csv_horrible, csv_suspect]:
	f.close()
