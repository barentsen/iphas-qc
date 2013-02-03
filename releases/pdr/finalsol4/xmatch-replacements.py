import pyfits
import os
import numpy as np
import logging
import multiprocessing
from multiprocessing import Pool

logging.basicConfig(level=logging.DEBUG, 
    format="%(asctime)s/%(levelname)s: %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S" )

# directory containing catalogues
IPHAS_OBSERVATIONS = '/home/gb/dev/iphas-qc/qcdata/iphas-qc.fits'
MERCAT_DIR = '/home/gb/tmp/iphas_sep2012_eglez/apm3.ast.cam.ac.uk/~eglez/iphas'
# Define the magnitude limits for photometry comparison
MAG_LIMITS = {'r': [14,18], 'i':[13,18], 'h':[13,18]}



class ZeropointOffset():

    def __init__(self, id1, id2):
        self.id1 = id1
        self.id2 = id2
        self.meta = pyfits.getdata(IPHAS_OBSERVATIONS, 1)

    def get_catalogue(self, fieldid):
        """
        Returns the location of the catalogue for a given field id

        """
        result = self.meta.field('mercat')[ self.meta.field('id') == fieldid ]
        if len(result) == 1:
            return MERCAT_DIR+'/'+result[0]
        else:
            raise Exception('Could not find mercat filename for %s in metadata table' % fieldid)

    def crossmatch(self, file1, file2):
        """
        Crossmatch two catalogues

        """
        # Concatenate multi-extension catalogues and crossmatch using stilts
        cmd = []
        cmd.append("stilts tcat in=%s multi=true ocmd='addcol RAd \"radiansToDegrees(RA)\"; addcol DECd \"radiansToDegrees(DEC)\";' out=/tmp/%s_concat1.fits > /dev/null" 
                    % (file1, self.id2) )
        cmd.append("stilts tcat in=%s multi=true ocmd='addcol RAd \"radiansToDegrees(RA)\"; addcol DECd \"radiansToDegrees(DEC)\";' out=/tmp/%s_concat2.fits > /dev/null" 
                    % (file2, self.id2) )

        # Remove blended sources from both concatenated catalogues
        # It is crucial to remove all objects which have neighbours within 3 arcsec!
        for number in [1,2]: 
            cmd.append("stilts tmatch1 progress=none matcher=sky "
                       + "values=\"RAd DECd\" params=3 action=keep0 "
                       + "in=/tmp/%s_concat%d.fits out=/tmp/%s_concat%d_deblend.fits > /dev/null" % (self.id2, number, self.id2, number) )

        # Crossmatch
        cmd.append("stilts tskymatch2 "
                      " in1=/tmp/%s_concat1_deblend.fits in2=/tmp/%s_concat2_deblend.fits" % (self.id2, self.id2) + 
                      " ra1='RAd' dec1='DECd'" +
                      " ra2='RAd' dec2='DECd'" +
                      " error=0.1 out=/tmp/%s_xmatch.fits 2> /dev/null" % (self.id2) )

        for c in cmd:
            os.system(c)

    def report(self, file1, file2):
        """
        Analyze the consistency of the crossmatched stars

        """
        # Count number of crossmatched stars
        d = pyfits.getdata('/tmp/%s_xmatch.fits' % self.id2, 1)
        c_star = ((d['rClass_1'] == -1) & (d['rClass_2'] == -1)
                    & (d['iClass_1'] == -1) & (d['iClass_2'] == -1)
                    & (d['hClass_1'] == -1) & (d['hClass_2'] == -1) )
        c_bright_star = ( c_star 
                          & (d['rApermag3_1'] > MAG_LIMITS['r'][0]) 
                          & (d['rApermag3_1'] < MAG_LIMITS['r'][1])
                          & (d['iApermag3_1'] > MAG_LIMITS['i'][0]) 
                          & (d['iApermag3_1'] < MAG_LIMITS['i'][1])
                          & (d['hApermag3_1'] > MAG_LIMITS['h'][0]) 
                          & (d['hApermag3_1'] < MAG_LIMITS['h'][1]) )
        n_stars = c_bright_star.sum()

        # Data structures to store comparison results per band
        median_diff = {}
        std_diff = {}
        idx_outliers, n_outliers = {}, {}

        # Compare photometric offsets per band
        for band in ['r', 'i', 'h']:
            # diff: array with magnitude differences
            diff = ( d[band+'Apermag3_1'][c_bright_star] 
                     - d[band+'Apermag3_2'][c_bright_star] )

            # Compute median and standard deviation
            median_diff[band] = np.median(diff)
            std_diff[band] = np.std(diff)

        # Write results
        csv = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
            (self.id1, self.id2, n_stars, \
                median_diff['r'], median_diff['i'], median_diff['h'], \
                std_diff['r'], std_diff['i'], std_diff['h'], \
                file1, file2)
        return csv

    def clean(self):
        # Clean
        cmd = []
        cmd.append("rm /tmp/%s_concat1.fits" % self.id2)
        cmd.append("rm /tmp/%s_concat2.fits" % self.id2)
        cmd.append("rm /tmp/%s_concat1_deblend.fits" % self.id2)
        cmd.append("rm /tmp/%s_concat2_deblend.fits" % self.id2)
        cmd.append("rm /tmp/%s_xmatch.fits" % self.id2)
        for c in cmd:
            os.system(c)

    def run(self):
        out = []

        logging.info("Comparing %s vs %s" % (self.id1, self.id2) )
        file1 = self.get_catalogue( self.id1 )
        file2 = self.get_catalogue( self.id2 )
        self.crossmatch(file1, file2)

        csv = self.report(file1, file2)

        self.clean()

        return csv

def run():
    replacements = open('../replacements.csv', 'r').readlines()
    id_ref = [line.split(',')[17].strip() for line in replacements[1:]]
    id_new = [line.split(',')[2].strip() for line in replacements[1:]]

    p = Pool(processes=3)
    results = p.imap(run_one, zip(id_ref, id_new))

    out = open('pdr-calib.csv', 'w')
    out.write('id_ref,id_new,n_stars,shift_r,shift_i,shift_h,std_r,std_i,std_h,file1,file2\n')
    for r in results:
        out.write(r)
        out.flush()
    out.close()

def run_one(input):
    id_ref, id_new = input
    zo = ZeropointOffset(id_ref, id_new)
    result = zo.run()
    return result

if __name__ == '__main__':
    run()
    #print run_one( ('0072o_dec2003', '0072o_jul2012') )
