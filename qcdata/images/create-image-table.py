"""
Walk through the IPHAS raw data directory and create a CSV table which links
the images, confidence maps and field numbers
"""
import os
import re
import logging
import pyfits
import numpy as np

def is_local():
    """Are we running locally or on the cluster?"""
    if os.uname()[1] == 'uhppc11.herts.ac.uk':
        return True
    return False


"""CONFIGURATION"""

# Initialize logging
logging.basicConfig( level=logging.INFO )

# Where are the images?
if is_local():
    datadir = '/media/0133d764-0bfe-4007-a9cc-a7b1f61c4d1d/iphas/'
else:
    datadir = '/car-data/gb/iphas/'
logging.info('Datadir assumed to be at '+datadir)

# Initialize output table
out = open('iphas-images.csv', 'w')
out.write('run,image,conf_ha,conf_r,conf_i\n')

# Confidence maps can have various different filenames
CONF_NAMES = {'ha': ['Ha_conf.fits', 'Ha_conf.fit', 
                    'Halpha_conf.fit',
                    'ha_conf.fits', 'ha_conf.fit', 
                    'h_conf.fits', 'h_conf.fit',
                    'Halpha:197_iphas_aug2003_cpm.fit', 
                    'Halpha:197_iphas_sep2003_cpm.fit',
                    'Halpha:197_iphas_oct2003_cpm.fit', 
                    'Halpha:197_iphas_nov2003_cpm.fit', 
                    'Halpha:197_nov2003b_cpm.fit', 
                    'Halpha:197_dec2003_cpm.fit',
                    'Halpha:197_jun2004_cpm.fit', 
                    'Halpha:197_iphas_jul2004a_cpm.fit',
                    'Halpha:197_iphas_jul2004_cpm.fit', 
                    'Halpha:197_iphas_aug2004a_cpm.fit',
                    'Halpha:197_iphas_aug2004b_cpm.fit', 
                    'Halpha:197_iphas_dec2004b_cpm.fit'], 
                'r': ['r_conf.fit', 'r_conf.fits', 
                    'r:214_iphas_aug2003_cpm.fit', 
                    'r:214_dec2003_cpm.fit', 
                    'r:214_iphas_nov2003_cpm.fit', 
                    'r:214_nov2003b_cpm.fit', 
                    'r:214_iphas_sep2003_cpm.fit',
                    'r:214_iphas_aug2004a_cpm.fit', 
                    'r:214_iphas_aug2004b_cpm.fit',
                    'r:214_iphas_jul2004a_cpm.fit', 
                    'r:214_iphas_jul2004_cpm.fit',
                    'r:214_jun2004_cpm.fit'],
                'i': ['i_conf.fit', 'i_conf.fits', 
                    'i:215_iphas_aug2003_cpm.fit', 
                    'i:215_dec2003_cpm.fit', 
                    'i:215_iphas_nov2003_cpm.fit', 
                    'i:215_nov2003b_cpm.fit', 
                    'i:215_iphas_sep2003_cpm.fit',
                    'i:215_iphas_aug2004a_cpm.fit', 
                    'i:215_iphas_aug2004b_cpm.fit',
                    'i:215_iphas_jul2004a_cpm.fit', 
                    'i:215_iphas_jul2004_cpm.fit',
                    'i:215_jun2004_cpm.fit']}



# Dict to hold the confidence maps for each filter/directory
confmaps = {'r' : {}, 'i' : {}, 'ha' : {}}

def get_confmap(mydir, band):
    """Return the name of the confidence map in directory 'mydir'"""
    assert( band in ['r', 'i', 'ha'] )

    # The result from previous function calls are stored in 'confmaps'
    if mydir not in confmaps[band].keys():

        # Some directories do not contain confidence maps
        if mydir == datadir+'iphas_nov2006c':
            candidatedir = datadir+'iphas_nov2006b'
        elif mydir == datadir+'iphas_jul2008':
            candidatedir = datadir+'iphas_aug2008'
        elif mydir == datadir+'iphas_oct2009':
            candidatedir = datadir+'iphas_nov2009'       
        elif mydir == datadir+'run10':
            candidatedir = datadir+'run11'
        elif mydir == datadir+'run13':
            candidatedir = datadir+'run12'
        else:
            candidatedir = mydir

        # Try all possible names
        for name in CONF_NAMES[band]: 
            candidate = candidatedir+'/'+name
            if os.path.exists(candidate):
                confmaps[band][mydir] = candidate # Success!
                continue

    # Return confidence map name if we found one, raise exception otherwise
    try:
        return confmaps[band][mydir]
    except KeyError:
        raise Exception('No confidence map found in directory %s' % mydir)


""" MAIN """
# The raw data dir contains 'special' sub-directories with exposures to ignore
directories_to_ignore = ['junk', 'badones', 'crap', '9thoct', \
                         'Uband', 'gband', 'slow']

for mydir in os.walk(datadir, followlinks=True):
    logging.info('Entering '+mydir[0])
    # We're ignoring certain directories
    if mydir[0].split('/')[-1] in directories_to_ignore:
        continue

    # Consider each file
    for filename in mydir[2]:
        # Images should be named "rnnnnnn.fit"
        if re.match('^r\d+.fit', filename):
            logging.debug("%s/%s" % (mydir[0], filename))
            image_path = os.path.join(mydir[0], filename)
            conf_path = get_confmap(mydir[0], 'i')

            conf_ha = get_confmap(mydir[0], 'ha')[len(datadir):]
            conf_r = get_confmap(mydir[0], 'r')[len(datadir):]
            conf_i = get_confmap(mydir[0], 'i')[len(datadir):]

            # Run number is the first part of the filename
            myrun = filename.split('.')[0][1:]
            # Write the details of this image
            out.write("%s,%s,%s,%s,%s\n" % \
                     (myrun, image_path[len(datadir):], conf_ha, conf_r, conf_i)) 

out.close()
