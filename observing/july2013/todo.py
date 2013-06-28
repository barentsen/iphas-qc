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


LON_FINISH = 60
PLANNER = fits.getdata('../iphas-planner.fits', 1)
IPHASQC = fits.getdata('../../qcdata/iphas-qc.fits', 1)

# Load definition of fields in the format required by the observing scripts
fields_list = open('../fields.txt', 'r').readlines()
FIELDS = dict(zip([m.split(' ')[0].split('_')[1] for m in fields_list], fields_list))

FILES = {}


def output_open():
    """Initiate the output files"""
    for ra in ['A', 'B', 'C']:
        FILES[str(ra)] = open('output/group%s.todo' % ra, 'w')


def output_close():
    # Close the output files
    for ra in FILES.keys():
        FILES[ra].close()


def add_field(infoline):
    """Write a field descriptor to the appropriate todo file"""
    # Obtain Right Ascension from field descriptor
    #ra = re.split("\W+", infoline)[1]
    dec = int(re.split("\W+", infoline)[5])
    if dec < 4:
        group = 'C'
    elif dec < 14:
        group = 'B'
    else:
        group = 'A'
    FILES[group].write(infoline)


if __name__ == "__main__":
    output_open()

    mylog = open('repeats.txt', 'w')
    mylog.write('IPHAS fields to be repeated in June 2013\n')
    mylog.write('========================================\n')
    mylog.write('\n')
    mylog.write('This is a list of B/C/D-quality fields at longitudes 25-{0}.\n'.format(LON_FINISH))
    mylog.write('\n')


    # Which longitude block do we want to finish?
    cond_finish = (PLANNER['l'] < LON_FINISH)
    cond_accept = (
                    IPHASQC['is_best']
                    & (IPHASQC['qflag'] != 'D')
                    & (IPHASQC['qflag'] != 'C')
                    & (IPHASQC['qflag'] != 'B')
                  )
    fields_todo = []

    for name in PLANNER['name'][cond_finish]:
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
