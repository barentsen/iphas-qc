import pyfits
import numpy as np
import os

obs = pyfits.getdata('../iphas-observations.fits', 1)
out = open('fieldpair-info.csv', 'w')
out.write("field,dir,n_matched,n_01,n_02,n_01_r,n_01_i,n_01_h,n_02_r,n_02_i,n_02_h,file1,file2\n")

mercat_dir = '/home/gb/tmp/iphas_sep2012_eglez/apm3.ast.cam.ac.uk/~eglez/iphas'

# Run over each observed field, and find same-run partners
for i, myfield in enumerate(obs['field']):
	if not myfield.endswith('o'):
		# Is there a partner?
		c_partner = (obs['field'] == myfield+"o") & \
					(obs['dir'] == obs['dir'][i])
		if np.any(c_partner):
			file1 = obs['mercat'][i]
			file2 = obs['mercat'][ np.argwhere(c_partner)[0,0] ]

		# Concatenate multi-extension catalogues and crossmatch
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

		# Compare the magnitudes
		n_stars_shifted_01 = {}
		n_stars_shifted_02 = {}

		limits = {'r': [14,18], 'i':[13,17], 'h':[13.5,17.5]}

		for band in ['r', 'i', 'h']:
			c_star = (d[band+'Class_1'] == -1) & (d[band+'Class_2'] == -1)
			c_bright_star = (c_star & (d[band+'Apermag3_1'] > limits[band][0]) & (d[band+'Apermag3_1'] < limits[band][1]))
			mag_diff = abs(d[band+'Apermag3_1'][c_bright_star] - d[band+'Apermag3_2'][c_bright_star])
			c_shifted_01 = (mag_diff > 0.1)
			n_stars_shifted_01[band] = c_shifted_01.sum()
			c_shifted_02 = (mag_diff > 0.2)
			n_stars_shifted_02[band] = c_shifted_02.sum()
				


		out.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
			(myfield, obs['dir'][i], n_stars, sum(n_stars_shifted_01.values()), sum(n_stars_shifted_02.values()), \
				n_stars_shifted_01['r'], n_stars_shifted_01['i'], n_stars_shifted_01['h'], \
				n_stars_shifted_02['r'], n_stars_shifted_02['i'], n_stars_shifted_02['h'], \
				file1, file2))

		out.flush()

out.close()
		
