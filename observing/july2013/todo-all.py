#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create observing todo files for July 2013"""
from __future__ import division, print_function, unicode_literals
from astropy.io import fits
import re

import logging
log = logging.getLogger(__name__)

__author__ = "Geert Barentsen"
__copyright__ = "Copyright, The Authors"
__credits__ = []


PLANNER = fits.getdata('../iphas-planner.fits', 1)
IPHASQC = fits.getdata('../../qcdata/iphas-qc.fits', 1)

# Load definition of fields in the format required by the observing scripts
fields_list = open('../fields.txt', 'r').readlines()
FIELDS = dict(zip([m.split(' ')[0].split('_')[1] for m in fields_list], fields_list))

FILES = {}


def output_open():
    """Initiate the output files"""
    for ra in [0,1,2,3,4,5,6,7,8,18,19,20,21,22,23]:
        FILES[str(ra)] = open('output-all/fields.%sh.todo' % ra, 'w')

def output_close():
    # Close the output files
    for ra in FILES.keys():
        FILES[ra].close()


ralog = {}
def add_field(infoline):
    """Write a field descriptor to the appropriate todo file"""
    # Obtain Right Ascension from field descriptor
    ra = re.split("\W+", infoline)[1]

    # Do not divide on/off exposures over bins
    myid = infoline[0:12]
    if ralog.has_key(myid):
        ra = ralog[myid]
    else:
        ralog[myid] = ra

    FILES[ra].write(infoline)


if __name__ == "__main__":
    output_open()

    mylog = open('repeats.txt', 'w')
    mylog.write('IPHAS fields to be repeated in June 2013\n')
    mylog.write('========================================\n')
    mylog.write('\n')
    mylog.write('This is a list of B/C/D-quality fields.\n')
    mylog.write('\n')


    cond_accept = (
                    IPHASQC['is_best']
                    & (IPHASQC['qflag'] != 'D')
                    & (IPHASQC['qflag'] != 'C')
                    & (IPHASQC['qflag'] != 'B')
                  )
    fields_todo = []

    for name in PLANNER['name']:
        field_no = name.split('_')[1]
        for myfield in [field_no, field_no+'o']:

            cond_field = (IPHASQC['field'] == myfield) & cond_accept
            n_accept = cond_field.sum()
            if n_accept > 1:
                assert('Impossible state: same field multiple times in DR')
            elif n_accept == 0:
                fields_todo.append(myfield)
                print( FIELDS[myfield] )
                add_field(FIELDS[myfield])
                myra = '{0}h{1:>2s}m'.format(re.split('\W+', FIELDS[myfield])[1],
                                             re.split('\W+', FIELDS[myfield])[2])
                mydec = '{0:+0d}d'.format(int(re.split('\W+', FIELDS[myfield])[5]))

                cond_reason = (IPHASQC['field'] == myfield) & IPHASQC['is_best']
                if cond_reason.sum() == 0:
                    mylog.write('{0:15s}{1:>6s} {2:>4s}    *MISSING FIELD*\n'.format(myfield,
                                                              myra,
                                                              mydec))
                else:
                    myfieldid = IPHASQC['id'][cond_reason][0]
                    qflag = IPHASQC['qflag'][cond_reason][0]
                    reason = IPHASQC['problems'][cond_reason][0]
                    

                    mylog.write('{0:15s}{1:>6s} {2:>4s} {3:3s}{4}\n'.format(myfieldid,
                                                                        myra,
                                                                        mydec,
                                                                        qflag,
                                                                        reason))

    mylog.write('\n')
    mylog.write('Total: {0} fields\n'.format(len(fields_todo)))

    mylog.close()
    output_close()
