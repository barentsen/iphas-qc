"""
Crossmatch fieldpairs to check the consistency of the photometry

This is an MPI-enabled script, i.e. run using
mpirun -np 8 python do-mosaic-mpi.py
"""
from mpi4py import MPI
import logging
import pyfits
import numpy as np
import os

# Setup MPI and logging
comm = MPI.COMM_WORLD
logging.basicConfig(level=logging.DEBUG, 
    format="%(asctime)s/W"+str(comm.rank)+"/"+MPI.Get_processor_name()+"/%(levelname)s: %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S" )

# Define the messages we'll be passing through MPI
TAG_GIVE_WORK = 801  # Worker waiting for instructions
TAG_CSV = 802        # CSV output
TAG_FINISHED = 850   # All work is done
TAG_DONE = 851   # All work is done

# directory containing catalogues
IPHAS_OBSERVATIONS = '../iphas-observations.fits'
MERCAT_DIR = '/home/gb/tmp/iphas_sep2012_eglez/apm3.ast.cam.ac.uk/~eglez/iphas'
# Define the magnitude limits for photometry comparison
MAG_LIMITS = {'r': [14,18], 'i':[13,18], 'h':[13,18]}


class FieldChecker():
    
    def __init__(self, field):
        self.field = field
        self.meta = pyfits.getdata(IPHAS_OBSERVATIONS, 1)

    def generate_pairs(self):
        """
        Figure out the most appropriate pairs to carry out the 
        validation of the photometry

        """
        pairs = []

        ids = self.meta.field('id')
        ids_done = []

        # Field identifiers
        c = (self.meta.field('field') == self.field) | (self.meta.field('field') == self.field+'o')

        # For each field realization, find the partner in the same month
        # if no partner in the same month exists, choose the best possible run
        for i, in np.argwhere(c):
            partner1 = ids[i]
            if partner1 in ids_done:
                continue

            # Choose the best partner
            # First approach: use the same-night offset field
            delta_jd = np.abs(self.meta.field('mjd')[i] - self.meta.field('mjd')[c])
            i_closest = np.argsort(delta_jd)[1] # Index 1, because 0 is self
            if delta_jd[i_closest] < 0.5:
                is_samenight = True
                partner2 = ids[c][i_closest]
                ids_done.append( partner2 ) # No need to repeat procedure for partner
            # Second approach: good-quality field with deepest rmode
            else:
                is_samenight = False
                # Good fields, avoiding self
                c2 = (c & self.meta.field('is_ok') 
                      & (self.meta.field('id') != partner1) )
                if c2.sum() > 0:
                    i_sorted_by_rmode = np.argsort( self.meta.field('rmode')[c2] )
                    partner2 = ids[c2][ i_sorted_by_rmode[-1] ]
                else:
                    continue # No good partner available

            ids_done.append( partner1 )            
            pairs.append( {'partner1':partner1, 
                           'partner2':partner2, 
                           'is_samenight':is_samenight} )

        return pairs

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
                    % (file1, self.field) )
        cmd.append("stilts tcat in=%s multi=true ocmd='addcol RAd \"radiansToDegrees(RA)\"; addcol DECd \"radiansToDegrees(DEC)\";' out=/tmp/%s_concat2.fits > /dev/null" 
                    % (file2, self.field) )

        # Remove blended sources from both concatenated catalogues
        # It is crucial to remove all objects which have neighbours within 3 arcsec!
        for number in [1,2]: 
            cmd.append("stilts tmatch1 progress=none matcher=sky "
                       + "values=\"RAd DECd\" params=3 action=keep0 "
                       + "in=/tmp/%s_concat%d.fits out=/tmp/%s_concat%d_deblend.fits > /dev/null" % (self.field, number, self.field, number) )

        # Crossmatch
        cmd.append("stilts tskymatch2 "
                      " in1=/tmp/%s_concat1_deblend.fits in2=/tmp/%s_concat2_deblend.fits" % (self.field, self.field) + 
                      " ra1='RAd' dec1='DECd'" +
                      " ra2='RAd' dec2='DECd'" +
                      " error=0.1 out=/tmp/%s_xmatch.fits 2> /dev/null" % (self.field) )

        for c in cmd:
            os.system(c)

    def report(self, file1, file2):
        """
        Analyze the consistency of the crossmatched stars

        """
        # Count number of crossmatched stars
        d = pyfits.getdata('/tmp/%s_xmatch.fits' % self.field, 1)
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

            # Count outliers
            median_offsets = abs(diff - median_diff[band])
            
            # Percentage level of outliers
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
        csv = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
            (n_stars, \
                total_outliers[5], total_outliers[10], total_outliers[20], \
                fraction_outliers[5], fraction_outliers[10], fraction_outliers[20], \
                n_outliers[5]['r'], n_outliers[5]['i'], n_outliers[5]['h'], \
                n_outliers[10]['r'], n_outliers[10]['i'], n_outliers[10]['h'], \
                n_outliers[20]['r'], n_outliers[20]['i'], n_outliers[20]['h'], \
                median_diff['r'], median_diff['i'], median_diff['h'], \
                std_diff['r'], std_diff['i'], std_diff['h'], \
                file1, file2)
        return csv

    def clean(self):
        # Clean
        cmd = []
        cmd.append("rm /tmp/%s_concat1.fits" % self.field)
        cmd.append("rm /tmp/%s_concat2.fits" % self.field)
        cmd.append("rm /tmp/%s_concat1_deblend.fits" % self.field)
        cmd.append("rm /tmp/%s_concat2_deblend.fits" % self.field)
        cmd.append("rm /tmp/%s_xmatch.fits" % self.field)
        for c in cmd:
            os.system(c)

    def run(self):
        out = []

        pairs = self.generate_pairs()
        logging.info("Pairs: %s" % pairs )
        for pair in pairs:
            logging.info("Comparing %s vs %s" % (pair['partner1'], pair['partner2']) )
            file1 = self.get_catalogue( pair['partner1'] )
            file2 = self.get_catalogue( pair['partner2'] )
            self.crossmatch(file1, file2)

            csv = self.report(file1, file2)
            out.append( '%s,%s,%s,%s' % 
                                (pair['partner1'], pair['partner2'], 
                                 pair['is_samenight'], csv) )
            if pair['is_samenight']:
                out.append( '%s,%s,%s,%s' % 
                                    (pair['partner2'], pair['partner1'], 
                                     pair['is_samenight'], csv) )

            self.clean()

        return out



def mpi_master():
    """
    Distributes the work

    """
    logging.info("Running on %d cores" % comm.size)

    iphas_largest_fieldnumber = 7635
    for fieldnumber in np.arange(1, iphas_largest_fieldnumber+1):
        myfield = '%04d' % fieldnumber
         # Wait for a worker to report for duty
        rank_done = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_GIVE_WORK)
        # Send the worker the details of the next field
        msg = myfield
        comm.send(msg, dest=rank_done)
        logging.info('Field %s sent to worker %s' % (myfield, rank_done))

    
    # Tell all workers we're finished
    for worker in range(2, comm.size):
        comm.send(TAG_FINISHED, dest=worker)
    for worker in range(2, comm.size):
        comm.recv(source=worker, tag=TAG_DONE)

    # Finally, kill off the writer
    comm.send(TAG_FINISHED, dest=1)
    return

def mpi_writer():
    """
    Writes results.

    """
    out = open('pairs.csv', 'w')
    out.write("field,partner,is_samenightpair,n_matched,n_outliers_5p,n_outliers_10p,n_outliers_20p"
            +",f_outliers_5p,f_outliers_10p,f_outliers_20p"
            +",n_5p_r,n_5p_i,n_5p_h,n_10p_r,n_10p_i,n_10p_h,n_20p_r,n_20p_i,n_20p_h"
            + ",med_dr,med_di,med_dh,std_dr,std_di,std_dh,file1,file2\n")

    while True:
        msg = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)

        if msg == TAG_FINISHED:
            return
        else:
            for line in msg:
                out.write(line)

        out.flush()

    out.close()

def mpi_worker():
    """
    Carries out the work.

    """
    while True:
        # Ask for work
        comm.send(comm.rank, dest=0, tag=TAG_GIVE_WORK)
        msg = comm.recv(source=0)
        if msg == TAG_FINISHED:
            comm.send(comm.rank, dest=0, tag=TAG_DONE)
            return

        # Perform work
        logging.debug("Message rcvd: \"%s\"" % msg)

        checker = FieldChecker(msg)
        csv = checker.run()
        comm.send(csv, dest=1)    

def mpi_run():
    """
    Main function.

    """
    if comm.rank == 0:
        mpi_master()
    elif comm.rank == 1:
        mpi_writer()
    else:
        mpi_worker()
    return

""" MAIN EXECUTION """
if __name__ == "__main__":
    mpi_run()
