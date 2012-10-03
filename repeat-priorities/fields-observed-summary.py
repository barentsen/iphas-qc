"""
This script assigns re-observation priorities to IPHAS fields.
"""
import pyfits
d = pyfits.getdata("../qcdata/scripts/iphas-fields-observed.fits", 1)


# Output files
output = [None, \
		  open("priority-1.txt", "w"), \
		  open("priority-2.txt", "w"), \
		  open("priority-3.txt", "w")]


def report(priority, field, label):
	""" Report a field with a given re-observation priority """
	output[priority].write("%s\t%s\n" % (field,label))


for i in range(1, 7636):
	fieldname = "%04d" % i
	for field in [fieldname, fieldname+"o"]:
		c = d['field'] == field
		
		# Check for zero observations of a field
		if c.sum() == 0:
			report(1, field, '"not a single run available"')
			continue
		
		# Check for fields with HORRIBLE seeing
		check = d['seeing_worst'][c] < 3.0
		if check.sum() == 0: 
			report(1, field, '"seeing > 3.0"')
			continue

		# Check for fields with HORRIBLE ellipticity
		check = d['ellipt_worst'][c] < 0.30
		if check.sum() == 0: 
			report(1, field, '"ellipt > 0.30"')
			continue

		# Check for fields with out-of-spec seeing
		check = d['seeing_worst'][c] <= 2.0
		if check.sum() == 0: 
			report(2, field, '"seeing > 2.0"')
			continue

		# Check for fields with out-of-spec elliptiticy
		check = d['ellipt_worst'][c] <= 0.20
		if check.sum() == 0: 
			report(2, field, '"ellipt > 0.20"')
			continue

		# Check for fields with out-of-spec airmass
		check = d['airmass_worst'][c] <= 2.0
		if check.sum() == 0: 
			report(2, field, '"airmass > 2.0"')
			continue

		spec = (d['seeing_worst'][c] <= 2.0) & (d['ellipt_worst'][c] <= 0.2)
		if spec.sum() == 0: 
			report(2, field, '"no good seeing/ellipt/airmass in same run"')
			continue

		# Check for fields with LARGE shifts compared to other surveys
		check = spec & ( (abs(d['sdss_r'][c]) > 1.0) | (abs(d['sdss_i'][c]) > 1.0) ) | (d['sdss_stars'][c] < 50)
		if check.sum() == 0: 
			report(3, field, '"large shift compared to SDSS"')
			continue

		check = spec & ( (abs(d['apass_r'][c]) > 1.0) | (abs(d['apass_i'][c]) > 1.0) ) | (d['apass_stars'][c] > 50)
		if check.sum() == 0: 
			report(3, field, '"large shift compared to APASS"')
			continue


# Close files
for i in [1,2]:
	output[i].close()
