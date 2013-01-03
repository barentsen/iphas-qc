"""
Fix coordinate errors

Coordinates of fields in iphas-observations.fits are determined by
the RA/DEC values of the r-band images in Mike's DQC files.
Occasionally these are "0:00:00.00 +00:00:00.0", but the values for
the H-alpha band can be used instead.
"""

import pyfits
import os

f = pyfits.open('mikes-dqc-data.fits')

for i in range(f[1].data.size):
    if ( f[1].data['name'][i].startswith('intphas')
         and f[1].data['name'][i].endswith('r')
         and ( f[1].data['ra'][i] == '0:00:00.00' 
               or f[1].data['dec'][i] == '+00:00:00.0')
        ):

        # Use the value for the H-alpha band instead
            f[1].data['ra'][i] = f[1].data['ra'][i-1]
            f[1].data['dec'][i] = f[1].data['dec'][i-1]


f.writeto('mikes-dqc-data.fits', clobber=True)


os.system('gzip mikes-dqc-data.fits')