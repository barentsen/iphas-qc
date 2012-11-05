"""
This script assigns re-observation priorities to IPHAS fields.
"""
from __future__ import division
import pyfits

# INPUT DATA = table with collated quality information
d = pyfits.getdata("../data/iphas-observations.fits", 1)





# Define the function to write a field to a given priority list

reportlog = {} # Dictionary with all repeat fields!
def report(priority, field, label):
	""" Report a field with a given re-observation priority and error label """

	reportlog[field] = {}
	reportlog[field]['priority'] = priority
	reportlog[field]['label'] = label

	# Was the on-field reported? If so: assign the highest priority to both!
	partner_field = field.replace('o','')
	if reportlog.has_key( partner_field ):
		partner_priority = reportlog[ partner_field ]['priority']
		new_priority = min(priority, partner_priority)

		# Update priorities
		reportlog[ partner_field ]['priority'] = new_priority
		reportlog[ field ]['priority'] = new_priority



def write_to_files():
	"""Write the output stored in 'reportlog' dictionary to text files """
	# Create output files
	output = [None, \
		  open("priority-1.txt", "w"), \
		  open("priority-2.txt", "w"), \
		  open("priority-3.txt", "w"), \
		  open("priority-4.txt", "w"), \
		  open("priority-5.txt", "w"), ]

	# Loop over all fields and write them to the correct file
	for field in sorted(reportlog.keys()):
		priority = reportlog[field]['priority']
		label = reportlog[field]['label']

		output[priority].write("intphas_%s\t%s\n" % (field, label))
		output[priority].flush()

	# Close files
	for i in [1,2,3,4,5]:
		output[i].close()


def print_summary():
	# Keep a count for the various error labels
	counter = {}
	for field in reportlog.keys():
		label = reportlog[field]['label']
		if counter.has_key(label):
			counter[label] += 1
		else:
			counter[label] = 1

	# Print a summary
	for key in counter.keys():
		print "%s: [+%d fields]" % (key, counter[key])



""" MAIN """

# The fields below would normally pass our checks, 
# but were added manually for various reasons
add_to_priority1 = ['3489', '3489o'] # Double images!
add_to_priority3 = ['3045', '3075', '3079o', '3142o', '3391', '3625o', '3752', '3767o', '3832o', '3857',
'2704']



# Loop over all field numbers to check the available observations
for i in range(1, 7636):
	fieldname = "%04d" % i
	for field in [fieldname, fieldname+"o"]:
		c = d['field'] == field


		""" MISSING / HORRIBLE FIELDS """

		# Check for zero observations of a field
		if c.sum() == 0:
			report(1, field, 'All attempts failed CASU quality checks')
			continue
		
		# Check for fields with HORRIBLE seeing
		check = d['seeing_max'][c].round(5) < 2.5
		if check.sum() == 0: 
			report(1, field, 'seeing > 2.5')
			continue

		# Check for fields with HORRIBLE ellipticity
		check = d['ellipt_max'][c].round(5) < 0.25
		if check.sum() == 0: 
			report(1, field, 'ellipt > 0.25')
			continue


		if field in add_to_priority1:
			report(1, field, 'Added manually')
			continue

		""" FIELDS OUT OF SPEC """

		# Check for fields with out-of-spec seeing
		check = d['seeing_max'][c].round(5) <= 2.0
		if check.sum() == 0: 
			report(2, field, 'seeing > 2.0')
			continue

		# Check for fields with out-of-spec elliptiticy
		check = d['ellipt_max'][c].round(5) <= 0.20
		if check.sum() == 0: 
			report(2, field, 'ellipt > 0.20')
			continue

		# Check for fields with out-of-spec airmass
		check = d['airmass_max'][c].round(5) <= 2.0
		if check.sum() == 0: 
			report(2, field, 'airmass > 2.0')
			continue

		# Check for fields with out-of-spec sky
		check = d['sky_max'][c] < 1500
		if check.sum() == 0: 
			report(4, field, 'sky > 1500')
			continue

		spec = (d['seeing_max'][c].round(5) <= 2.0) \
				& (d['ellipt_max'][c].round(5) <= 0.20) \
				& (d['airmass_max'][c].round(5) <= 2.0) \
				& (d['sky_max'][c] < 1500)
		if spec.sum() == 0: 
			report(2, field, 'multiple constraints violated')
			continue



		""" GAIN VARIATIONS OR FRINGING PROBLEMS """

		check = spec & ( d['n_outliers_20p'][c] < 50 )
		if check.sum() == 0: 
			report(3, field, 'n_outliers_20p > 50 (gain variation or fringing)')
			continue

		check = spec & ( d['n_outliers_10p'][c] < 200 )
		if check.sum() == 0: 
			report(3, field, 'n_outliers_10p > 200 (gain variation or fringing)')
			continue


		if field in add_to_priority3:
			report(3, field, 'Added manually')
			continue

		""" SPARSE FIELDS """
		
		check = spec & ( d['f_stars_faint'][c] > 10.0 )
		if check.sum() == 0: 
			report(4, field, 'f_stars_faint < 10% (sparse)')
			continue

		check = spec & ( d['n_stars'][c] > 500 )
		if check.sum() == 0: 
			report(4, field, 'n_stars < 500 (sparse)')
			continue


		#check = spec & (d['r90p'][c] > 19.5)
		#if check.sum() == 0: 
		#	report(3, field, '"Sparse: Q90(r\') < 19.5"')
		#	continue


		""" LARGE CALIBRATION SHIFTS (LOWEST PRIORITY) """

		check = spec & ( 
					(d['sdss_stars'][c] < 50) | ( (abs(d['sdss_r'][c]) < 0.5) & (abs(d['sdss_i'][c]) < 0.5) ) )
		if check.sum() == 0: 
			report(5, field, 'sdss_r > 0.5 or sdss_i > 0.5')
			continue

		check = spec & (
					( d['apass_stars'][c] < 50) | ( (abs(d['apass_r'][c]) < 0.5) & (abs(d['apass_i'][c]) < 0.5) ) )
		if check.sum() == 0: 
			report(5, field, 'apass_r > 0.5 or apass_i > 0.5')
			continue

		# Check for fields with out-of-spec airmass
		check = d['airmass_max'][c].round(5) <= 1.7
		if check.sum() == 0: 
			report(5, field, 'airmass > 1.7')
			continue


write_to_files()
print_summary()
