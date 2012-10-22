"""
This script assigns re-observation priorities to IPHAS fields.
"""
from __future__ import division
import pyfits
d = pyfits.getdata("../data/iphas-observations.fits", 1)


f = open('../data/gotterdammerung/fields-done-in-fall-2012.txt', 'r')
fields_done_fall2012 = [l.strip() for l in f.readlines()]

def is_done(field):
	# Check if a field was successfully observed in the most recent runs
	if field in fields_done_fall2012:
		return True
	return False


# Create output files
output = [None, \
		  open("priority-1.txt", "w"), \
		  open("priority-2.txt", "w"), \
		  open("priority-3.txt", "w")]


# Writes a field to a given priority list
counter = {}
def report(priority, field, label):
	""" Report a field with a given re-observation priority """
	if is_done(field):
		return
	output[priority].write("intphas_%s\t%s\n" % (field,label))
	output[priority].flush()

	# Keep a count for the various error labels
	if counter.has_key(label):
		counter[label] += 1
	else:
		counter[label] = 1


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
		check = d['seeing_max'][c] < 2.5
		if check.sum() == 0: 
			report(1, field, '"seeing > 2.5 in all attempts"')
			continue

		# Check for fields with HORRIBLE ellipticity
		check = d['ellipt_max'][c] < 0.25
		if check.sum() == 0: 
			report(1, field, '"ellipt > 0.25 in all attempts"')
			continue


		""" FIELDS OUT OF SPEC """

		# Check for fields with out-of-spec seeing
		check = d['seeing_max'][c] <= 2.0
		if check.sum() == 0: 
			report(2, field, '"seeing > 2.0"')
			continue

		# Check for fields with out-of-spec elliptiticy
		check = d['ellipt_max'][c] <= 0.20
		if check.sum() == 0: 
			report(2, field, '"ellipt > 0.20"')
			continue

		# Check for fields with out-of-spec airmass
		check = d['airmass_max'][c] <= 2.0
		if check.sum() == 0: 
			report(2, field, '"airmass > 2.0"')
			continue

		# Check for fields with out-of-spec sky
		check = d['sky_max'][c] < 1500
		if check.sum() == 0: 
			report(2, field, '"sky > 1500"')
			continue

		spec = (d['seeing_max'][c] <= 2.0) & (d['ellipt_max'][c] <= 0.20) \
				& (d['airmass_max'][c] <= 2.0) & (d['sky_max'][c] < 2000)
		# & (d['sky_max'][c] < 2000)
		if spec.sum() == 0: 
			report(2, field, '"multiple constraints violated"')
			continue



		""" SPARSE FIELDS """
		
		check = spec & ( d['f_stars_faint'][c] > 10.0 )
		if check.sum() == 0: 
			report(3, field, '"f_stars_faint < 10% (sparse)"')
			continue

		check = spec & ( d['n_stars'][c] > 500 )
		if check.sum() == 0: 
			report(3, field, '"n_stars < 500 (sparse)"')
			continue

		#check = spec & (d['r90p'][c] > 19.5)
		#if check.sum() == 0: 
		#	report(3, field, '"Sparse: Q90(r\') < 19.5"')
		#	continue


		""" GAIN VARIATIONS OR FRINGING PROBLEMS """

		check = spec & ( d['n_outliers_20p'][c] < 20 )
		if check.sum() == 0: 
			report(3, field, '"n_outliers_20p > 20 (gain variation or fringing)"')
			continue

		check = spec & ( d['n_outliers_10p'][c] < 200 )
		if check.sum() == 0: 
			report(3, field, '"n_outliers_10p > 200 (gain variation or fringing)"')
			continue


		""" LARGE CALIBRATION SHIFTS """

		check = spec & ( 
					(d['sdss_stars'][c] < 50) | ( (abs(d['sdss_r'][c]) < 0.5) & (abs(d['sdss_i'][c]) < 0.5) ) )
		if check.sum() == 0: 
			report(3, field, '"sdss_r > 0.5 or sdss_i > 0.5"')
			continue

		check = spec & (
					( d['apass_stars'][c] < 50) | ( (abs(d['apass_r'][c]) < 0.5) & (abs(d['apass_i'][c]) < 0.5) ) )
		if check.sum() == 0: 
			report(3, field, '"apass_r > 0.5 or apass_i > 0.5"')
			continue


# Close files
for i in [1,2,3]:
	output[i].close()

# Print a summary
for key in counter.keys():
	print "%s: [+%d fields]" % (key, counter[key])
