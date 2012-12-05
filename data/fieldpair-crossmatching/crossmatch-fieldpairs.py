"""Crossmatch fieldpairs and compute magnitude offsets and number of outliers"""
import pyfits
import numpy as np
import os


""" CONFIGURATION """

# List of observations and directory containing catalogues
obs = pyfits.getdata('../iphas-observations.fits', 1)
mercat_dir = '/home/gb/tmp/iphas_sep2012_eglez/apm3.ast.cam.ac.uk/~eglez/iphas'

# Define the magnitude limits for photometry comparison
limits = {'r': [14,18], 'i':[13,17], 'h':[13.5,17.5]}

# Create output file
out = open('fieldpair-info.csv', 'w')
out.write("field,dir,n_matched,n_outliers_5p,n_outliers_10p,n_outliers_20p" \
			+",f_outliers_5p,f_outliers_10p,f_outliers_20p" \
			+",n_5p_r,n_5p_i,n_5p_h,n_10p_r,n_10p_i,n_10p_h,n_20p_r,n_20p_i,n_20p_h" \
			+ ",med_dr,med_di,med_dh,std_dr,std_di,std_dh,file1,file2\n")


""" START CROSSMATCHING """ 

# Run over each observed field, and find same-run partners
for i, myfield in enumerate(obs['field']):
	if not myfield.endswith('o'):
		# Is there a partner?
		c_partner = (obs['field'] == myfield+"o") & \
					(obs['dir'] == obs['dir'][i])
		if np.any(c_partner):
			file1 = obs['mercat'][i]
			file2 = obs['mercat'][ np.argwhere(c_partner)[0,0] ]

		# Concatenate multi-extension catalogues and crossmatch using stilts
		cmd = []
		cmd.append("rm /tmp/concat1.fits /tmp/concat2.fits /tmp/xmatch.fits")
		cmd.append("stilts tcat in=%s/%s multi=true out=/tmp/concat1.fits" 
					% (mercat_dir, file1))
		cmd.append("stilts tcat in=%s/%s multi=true out=/tmp/concat2.fits" 
					% (mercat_dir, file2))
		#cmd.append("stilts tskymatch2"
		#			  " in1=/tmp/concat1.fits in2=/tmp/concat2.fits" + 
		#			  " ra1='radiansToDegrees(RA)' dec1='radiansToDegrees(DEC)'" +
		#			  " ra2='radiansToDegrees(RA)' dec2='radiansToDegrees(DEC)'" +
		#			  " error=0.1 out=/tmp/xmatch.fits")
		cmd.append("stilts tskymatch2"
					  " in1=/tmp/concat1.fits in2=/tmp/concat2.fits" + 
					  " ra1='radiansToDegrees(RA)' dec1='radiansToDegrees(DEC)'" +
					  " ra2='radiansToDegrees(RA)' dec2='radiansToDegrees(DEC)'" +
					  " error=0.1 out=/tmp/xmatch.fits")

		for c in cmd:
			os.system(c)

		# Count number of crossmatched stars
		d = pyfits.getdata('/tmp/xmatch.fits', 1)
		c_star = ((d['rClass_1'] == -1) & (d['rClass_2'] == -1)
					& (d['iClass_1'] == -1) & (d['iClass_2'] == -1)
					& (d['hClass_1'] == -1) & (d['hClass_2'] == -1) )
		c_bright_star = ( c_star 
						  & (d['rApermag3_1'] > limits['r'][0]) & (d['rApermag3_1'] < limits['r'][1])
						  & (d['iApermag3_1'] > limits['i'][0]) & (d['iApermag3_1'] < limits['i'][1])
						  & (d['hApermag3_1'] > limits['h'][0]) & (d['hApermag3_1'] < limits['h'][1]) )
		n_stars = c_bright_star.sum()



		# Data structure to store photometry comparison results per band
		median_diff = {}
		std_diff = {}
		idx_outliers, n_outliers = {}, {}

		# Compare photometric offsets per band
		for band in ['r', 'i', 'h']:
			# Select the stellar objects within the given magnitude limits
			#c_star = (d[band+'Class_1'] == -1) & (d[band+'Class_2'] == -1)
			#c_bright_star = ( c_star 
			#				  & (d[band+'Apermag3_1'] > limits[band][0]) 
			#				  & (d[band+'Apermag3_1'] < limits[band][1])
			#				)
			# diff: array with magnitude differences
			diff = d[band+'Apermag3_1'][c_bright_star] - d[band+'Apermag3_2'][c_bright_star]
			# Compute median and standard deviation
			median_diff[band] = np.median(diff)
			std_diff[band] = np.std(diff)
			# Count outliers
			median_offsets = abs(diff - median_diff[band])
			
			# Percentage level of offset
			for plevel in [5, 10, 20]:
				if not idx_outliers.has_key(plevel): idx_outliers[plevel] = {}
				if not n_outliers.has_key(plevel): n_outliers[plevel] = {}
				idx_outliers[plevel][band] = (median_offsets > plevel/100.)
				n_outliers[plevel][band] = idx_outliers[plevel][band].sum()

				
		# Count unique number of stars having outliers in one or more bands
		total_outliers, fraction_outliers = {}, {}
		for plevel in [5, 10, 20]:
			total_outliers[plevel] = (idx_outliers[plevel]['r'] \
									  | idx_outliers[plevel]['i'] \
									  | idx_outliers[plevel]['h']).sum()
			fraction_outliers[plevel] = 100*total_outliers[plevel] / float(n_stars)



		# Write results
		out.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
			(myfield, obs['dir'][i], n_stars, \
				total_outliers[5], total_outliers[10], total_outliers[20], \
				fraction_outliers[5], fraction_outliers[10], fraction_outliers[20], \
				n_outliers[5]['r'], n_outliers[5]['i'], n_outliers[5]['h'], \
				n_outliers[10]['r'], n_outliers[10]['i'], n_outliers[10]['h'], \
				n_outliers[20]['r'], n_outliers[20]['i'], n_outliers[20]['h'], \
				median_diff['r'], median_diff['i'], median_diff['h'], \
				std_diff['r'], std_diff['i'], std_diff['h'], \
				file1, file2))

		out.flush()

		# Keep a fits file with the matches for debugging
		stilts_cond = ("select \"rClass_1 == -1 & iClass_1 == -1 & hClass_1 == -1 " +
					  " & rClass_2 == -1 & iClass_2 == -1 & hClass_2 == -1 " +
					  " & rApermag3_1 > 14 & rApermag3_1 < 18 " +
					  " & iApermag3_1 > 13 & iApermag3_1 < 17 " +
					  " & hApermag3_1 > 13.5 & hApermag3_1 < 17.5\"")

		stilts_cond2 = ("addcol dr \"rApermag3_1 - rApermag3_2 - %.3f \";" % median_diff['r'] +
						"addcol di \"iApermag3_1 - iApermag3_2 - %.3f \";" % median_diff['i'] +
						"addcol dh \"hApermag3_1 - hApermag3_2 - %.3f \";" % median_diff['h'] +
						"addcol is_outlier_5p \"dr > 0.05 || di > 0.05 || dh > 0.05\"; " +
						"addcol is_outlier_10p \"dr > 0.1 || di > 0.1 || dh > 0.1\"; " +
						"addcol is_outlier_20p \"dr > 0.2 || di > 0.2 || dh > 0.2\"; " )

		cmd = ("stilts tcat in=/tmp/xmatch.fits" +
				   " icmd='%s' " % stilts_cond +
				   " ocmd='%s' " % stilts_cond2 +
				   " out=/home/gb/tmp/fieldpairs/%s_%s.fits" % (obs['dir'][i], myfield) )
		os.system(cmd)


""" WRITE RESULTS AND FINISH """ 
out.close()
		
