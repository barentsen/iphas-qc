"""
Crossmatch IPHAS fieldpairs to check the consistency of the photometry

This is an MPI-enabled script, i.e. run using
mpirun -np 8 nice python crossmatch-mpi.py
"""
from mpi4py import MPI
import logging
from astropy.io import fits as pyfits
import numpy as np
import os
from matplotlib import pyplot as plt

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
IPHAS_OBSERVATIONS = '../iphas-qc.fits'
MERCAT_DIR = '/car-data/gb/iphas-dr2-rc3/bandmerged'
PLOT_DIR = '/home/gb/tmp/iphas-quickphot'
# Define the magnitude limits for photometry comparison
MAG_LIMITS = {'r': [14,18], 'i':[13,18], 'h':[13,18]}

STILTS = 'nice java -Xmx2000M -XX:+UseConcMarkSweepGC -jar /home/gb/dev/iphas-dr2/dr2/lib/stilts.jar'

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
                    logging.warning('No partner for %s' % partner1)
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
        return os.path.join(MERCAT_DIR, fieldid+'.fits')

    def crossmatch(self, file1, file2):
        """
        Crossmatch two catalogues

        """
        cmd = []
        # Crossmatch
        cmd.append("%s tmatch2 matcher=sky " % STILTS +
                      " in1=%s in2=%s" % (file1, file2) + 
                      " icmd1='select \"(errBits == 0) & (pStar > 0.2) & (r < 19) & (i < 19) & (ha < 19)\";' " +
                      " icmd2='select \"(errBits == 0) & (pStar > 0.2) & (r < 19) & (i < 19) & (ha < 19)\";' " +
                      " values1='ra dec'" +
                      " values2='ra dec'" +
                      " params=0.5 out=/tmp/%s_xmatch.fits 2> /dev/null" % (self.field) )

        for c in cmd:
            os.system(c)

    def plot(self, partner1, partner2):
        output_filename = PLOT_DIR + '/' + partner1 + '.png'

        fig = plt.figure(figsize=(8,8))
        fig.suptitle('%s vs %s (median subtracted)' % (partner1, partner2), fontsize=22)
        fig.subplots_adjust(left=0.08, bottom=0.07, right=0.96, top=0.92,
                            wspace=0, hspace=0)
                
        labels = ['Ha', "r", "i"]

        # Count number of crossmatched stars
        d = pyfits.getdata('/tmp/%s_xmatch.fits' % self.field, 1)   
        for idx, band in enumerate(['h', 'r', 'i']):
            ax = fig.add_subplot(3, 1, idx+1)

            m1 = d[band+'Apermag3_1']
            m2 = d[band+'Apermag3_2']
            diff = m1 - m2
            med = np.median(diff)

            c = (m1 > MAG_LIMITS[band][0]) & (m1 < MAG_LIMITS[band][1]-1)
            c_outlier_10p = (diff[c] - med) > 0.1
            c_outlier_20p = (diff[c] - med) > 0.2
            #if (c_outlier_10p.sum() > 20) or (c_outlier_20p.sum() > 10):
            #    ax.set_axis_bgcolor('#FFB073') # Orange
            #if (c_outlier_10p.sum() > 50) or (c_outlier_20p.sum() > 15):
            #    ax.set_axis_bgcolor('#FF7373') # Red

            ax.scatter(m1, diff - med, linewidth=0, facecolor='black', 
                                        alpha=0.7, s=4, marker='o')

            ax.set_xlim([12.5, 20.5])
            ax.set_ylim([-0.25, +0.25])
            ax.set_xlabel('Magnitude')
            ax.text(12.7, 0.2, '%s' % labels[idx], fontsize=20,
                    verticalalignment='top')

        fig.savefig(output_filename, dpi=75)
        fig.clf()
        plt.close()

    def report(self, file1, file2):
        """
        Analyze the consistency of the crossmatched stars

        """
        # Count number of crossmatched stars
        d = pyfits.getdata('/tmp/%s_xmatch.fits' % self.field, 1)
        c_bright_star = (   (d['r_1'] > MAG_LIMITS['r'][0]) 
                          & (d['r_1'] < MAG_LIMITS['r'][1])
                          & (d['i_1'] > MAG_LIMITS['i'][0]) 
                          & (d['i_1'] < MAG_LIMITS['i'][1])
                          & (d['ha_1'] > MAG_LIMITS['h'][0]) 
                          & (d['ha_1'] < MAG_LIMITS['h'][1]) )
        n_stars = c_bright_star.sum()

        # Data structures to store comparison results per band
        median_diff = {}
        std_diff = {}
        idx_outliers, n_outliers = {}, {}

        # Compare photometric offsets per band
        for band in ['r', 'i', 'ha']:
            # diff: array with magnitude differences
            diff = ( d[band+'_1'][c_bright_star] 
                     - d[band+'_2'][c_bright_star] )

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
                                      | idx_outliers[plevel]['ha']).sum()
            if n_stars > 0:
                fraction_outliers[plevel] = 100*total_outliers[plevel] / float(n_stars)
            else:
                fraction_outliers[plevel] = ''

        # Write results
        csv = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
            (n_stars, \
                total_outliers[5], total_outliers[10], total_outliers[20], \
                fraction_outliers[5], fraction_outliers[10], fraction_outliers[20], \
                n_outliers[5]['r'], n_outliers[5]['i'], n_outliers[5]['ha'], \
                n_outliers[10]['r'], n_outliers[10]['i'], n_outliers[10]['ha'], \
                n_outliers[20]['r'], n_outliers[20]['i'], n_outliers[20]['ha'], \
                median_diff['r'], median_diff['i'], median_diff['ha'], \
                std_diff['r'], std_diff['i'], std_diff['ha'], \
                file1, file2)
        return csv

    def clean(self):
        # Clean
        cmd = []
        cmd.append("rm /tmp/%s_xmatch.fits" % self.field)
        for c in cmd:
            os.system(c)

    def run(self):
        out = []

        pairs = self.generate_pairs()
        logging.info("Pairs: %s" % pairs )
        for pair in pairs:

            output_filename = PLOT_DIR + '/' + pair['partner1'] + '.png'
            if os.path.exists(output_filename):
                continue

            logging.info("Comparing %s vs %s" % (pair['partner1'], pair['partner2']) )
            file1 = self.get_catalogue( pair['partner1'] )
            file2 = self.get_catalogue( pair['partner2'] )
            self.crossmatch(file1, file2)

            csv = self.report(file1, file2)
            out.append( '%s,%s,%s,%s' % 
                                (pair['partner1'], pair['partner2'], 
                                 pair['is_samenight'], csv) )
            #self.plot(pair['partner1'], pair['partner2'])

            if pair['is_samenight']:
                out.append( '%s,%s,%s,%s' % 
                                    (pair['partner2'], pair['partner1'], 
                                     pair['is_samenight'], csv) )
                #self.plot(pair['partner2'], pair['partner1'])

            self.clean()

        return out



def mpi_master():
    """
    Distributes the work

    """
    logging.info("Running on %d cores" % comm.size)

    iphas_largest_fieldnumber = 7635
    #iphas_largest_fieldnumber = 5
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
    out = open('/home/gb/dev/iphas-qc/qcdata/fieldpair-crossmatching/pairs-new.csv', 'w')
    out.write("id,id_partner,is_samenightpair,n_matched,n_outliers_5p,n_outliers_10p,n_outliers_20p"
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

        try:
            checker = FieldChecker(msg)
            csv = checker.run()
            comm.send(csv, dest=1)
        except Exception, e:
            logging.error('Aborted %s: %s' % (msg, str(e)))
        

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
    """
    checker = FieldChecker('7000')
    csv = checker.run()
    print csv
    """
    """
    from multiprocessing import Pool

    qc = pyfits.getdata(IPHAS_OBSERVATIONS, 1)
    #c = qc.field('is_best') & (qc.field('qflag') == "D")
    c = qc.field('is_dr2') & qc.field('is_anchor')
    fields = set([f[0:4] for f in qc.field('field')[c]])
    p = Pool(processes=8)
    p.map(do, fields)
    """

    

