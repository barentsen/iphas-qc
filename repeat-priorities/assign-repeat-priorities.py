"""
This script assigns re-observation priorities to IPHAS fields.
"""
from __future__ import division
import pyfits
d = pyfits.getdata("../qcdata/scripts/iphas-observations.fits", 1)


# Hack: allow to check which fields were successfully observed in the most recent runs
f = open('../qcdata/scripts/gotterdammerung/fields-done-in-fall-2012.txt', 'r')
fields_done_fall2012 = [l.strip() for l in f.readlines()]

def is_done(field):
	if field in fields_done_fall2012:
		return True
	return False


# Priorities: 1 = outside spec, 2 = barely inside spec, 3 = nice to improve
output = [None, \
		  open("priority-1.txt", "w"), \
		  open("priority-2.txt", "w"), \
		  open("priority-3.txt", "w")]


# Writes a field to a given priority list
def report(priority, field, label):
	""" Report a field with a given re-observation priority """
	if is_done(field):
		return
	output[priority].write("%s\t%s\n" % (field,label))


# Loop over all field numbers to check the available observations
for i in range(1, 7636):
	fieldname = "%04d" % i
	for field in [fieldname, fieldname+"o"]:
		c = d['field'] == field
		

		""" MISSING / HORRIBLE FIELDS """

		# Check for zero observations of a field
		if c.sum() == 0:
			report(1, field, '"All attempts failed CASU quality checks"')
			continue
		
		# Check for fields with HORRIBLE seeing
		check = d['seeing_max'][c] < 3.0
		if check.sum() == 0: 
			report(1, field, '"seeing > 3.0 in all attempts"')
			continue

		# Check for fields with HORRIBLE ellipticity
		check = d['ellipt_max'][c] < 0.30
		if check.sum() == 0: 
			report(1, field, '"ellipt > 0.30 in all attempts"')
			continue


		""" FIELDS OUT OF SPEC """

		# Check for fields with out-of-spec seeing
		check = d['seeing_max'][c] <= 2.0
		if check.sum() == 0: 
			report(2, field, '"seeing > 2.0 in all attempts"')
			continue

		# Check for fields with out-of-spec elliptiticy
		check = d['ellipt_max'][c] <= 0.20
		if check.sum() == 0: 
			report(2, field, '"ellipt > 0.2 in all attempts"')
			continue

		# Check for fields with out-of-spec airmass
		check = d['airmass_max'][c] <= 2.0
		if check.sum() == 0: 
			report(2, field, '"airmass > 2.0 in all attempts"')
			continue

		spec = (d['seeing_max'][c] <= 2.0) & (d['ellipt_max'][c] <= 0.2) & (d['airmass_max'][c] <= 2.0)
		if spec.sum() == 0: 
			report(2, field, '"seeing/ellipt/airmass out of spec in all attempts"')
			continue



		""" SPARSE FIELDS """


		check = spec & ( d['n_stars'][c] > 500 )
		if check.sum() == 0: 
			report(3, field, '"Sparse: less than 500 stellar objects"')
			continue

		
		fraction20 = d['n_stars_gt20'][c] / d['n_stars'][c]
		check = spec & ( ( fraction20 ) > 0.01 )
		if check.sum() == 0: 
			report(3, field, '"Sparse: less than 1% of stellar objects are fainter than r > 20"')
			continue

		check = spec & (d['r90p'][c] > 19)
		if check.sum() == 0: 
			report(3, field, '"Sparse: Q90(r\') < 19"')
			continue


		""" GAIN VARIATIONS """

		#check = spec & ( d['n_stars_10p_shift'][c] < 50 )
		#if check.sum() == 0: 
		#	report(3, field, '"Gain variation: >50 stars shifted by 0.1 mag between on/off fields"')
		#	continue

		check = spec & ( d['n_stars_20p_shift'][c] < 100 )
		if check.sum() == 0: 
			report(3, field, '"Gain variation: >100 stars shifted by 0.2 mag between on/off fields"')
			continue


		""" LARGE CALIBRATION SHIFTS """

		check = spec & ( 
					(d['sdss_stars'][c] < 50) | ( (abs(d['sdss_r'][c]) < 1.0) & (abs(d['sdss_i'][c]) < 1.0) ) )
		if check.sum() == 0: 
			report(3, field, '"Suspect: calibration off by >1 mag compared to Sloan DR9"')
			continue

		check = spec & (
					( d['apass_stars'][c] < 50) | ( (abs(d['apass_r'][c]) < 1.0) & (abs(d['apass_i'][c]) < 1.0) ) )
		if check.sum() == 0: 
			report(3, field, '"Suspect: calibration off by >1 mag compared to APASS"')
			continue


# Close files
for i in [1,2,3]:
	output[i].close()
