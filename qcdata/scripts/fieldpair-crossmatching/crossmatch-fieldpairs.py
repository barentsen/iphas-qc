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
		n_stars = c_star.sum()

		# Data structure to store photometry comparison results per band
		median_diff = {}
		std_diff = {}
		n_outliers_5p = {}
		n_outliers_10p = {}
		n_outliers_20p = {}		

		# Compare photometric offsets per band
		for band in ['r', 'i', 'h']:
			# Select the stellar objects within the given magnitude limits
			c_star = (d[band+'Class_1'] == -1) & (d[band+'Class_2'] == -1)
			c_bright_star = ( c_star 
							  & (d[band+'Apermag3_1'] > limits[band][0]) 
							  & (d[band+'Apermag3_1'] < limits[band][1])
							)
			# diff: array with magnitude differences
			diff = d[band+'Apermag3_1'][c_bright_star] - d[band+'Apermag3_2'][c_bright_star]
			# Compute median and standard deviation
			median_diff[band] = np.median(diff)
			std_diff[band] = np.std(diff)
			# Count outliers
			median_offsets = abs(diff - median_diff[band])
			n_outliers_5p[band] = (median_offsets > 0.05).sum()
			n_outliers_10p[band] = (median_offsets > 0.1).sum()
			n_outliers_20p[band] = (median_offsets > 0.2).sum()
				

		# Write results
		out.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
			(myfield, obs['dir'][i], n_stars, \
				sum(n_outliers_5p.values()), sum(n_outliers_10p.values()), sum(n_outliers_20p.values()), \
				n_outliers_5p['r'], n_outliers_5p['i'], n_outliers_5p['h'], \
				n_outliers_10p['r'], n_outliers_10p['i'], n_outliers_10p['h'], \
				n_outliers_20p['r'], n_outliers_20p['i'], n_outliers_20p['h'], \
				median_diff['r'], median_diff['i'], median_diff['h'], \
				std_diff['r'], std_diff['i'], std_diff['h'], \
				file1, file2))

		out.flush()


""" WRITE RESULTS AND FINISH """ 
out.close()
		
