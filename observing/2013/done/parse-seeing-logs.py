#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Parses the output of 'get_seeing.perl' and write a list of fields done.

Seeing log files gives us the file number, FWHM in pixel, FWHM in arcsec, 
ellipticity, sky background
"""                                                 
from __future__ import division, print_function, unicode_literals 

import re
import numpy as np
import os
from astropy.io import ascii
from astropy import log


def parse_log(filename):
    """Reads a single seeing_xxxxxx.log file.

    Returns
    -------
    A list of CSV-formatted strings.
    """
    output = []
    if not re.match("seeing_\d+.log", filename.split('/')[-1]):
        raise Exception('Unexpected filename: '+filename)
    night = filename.split('/')[-1][7:15]

    with open(filename, 'r') as myfile:
        for line in myfile.readlines():
            fields = re.split('\s+', line)
            if len(fields) > 7 and fields[7] == 'sources':
                run = fields[0].split('.')[0]
                seeing = fields[2]
                ellipt = fields[3]
                sky = fields[4]
                sources = fields[6]
                field = fields[9]
                filt = fields[10]

                csv_line = ("%s,%s,%s,%s,%s,%s,%s,%s\n" % 
                    (night, run, field, filt, seeing, ellipt, sky, sources))
                output.append(csv_line)
    return output


def interpret_logs(csv_filename):
    """Returns a list of fields completed successfully."""
    logdata = ascii.read(csv_filename)
    fields_done = []
    current_field = "" 
    for i, row in enumerate(logdata):

        if row['field'].startswith('intphas'):
            myfield = row['field'].split('_')[1]  # remove intphas prefix

            if myfield != current_field:
                current_field = myfield
                l_filters, l_seeing, l_ellipt, l_sky, l_sources = (
                                                        [], [], [], [], [])
            
            l_filters.append(row['filter'])
            l_seeing.append(row['seeing'])
            l_ellipt.append(row['ellipt'])
            l_sky.append(row['sky'])
            l_sources.append(row['sources'])

            if len(l_filters) == 3 and l_filters == ['Ha', 'r', 'i']:
                # Does the observation statisfy the quality constraints?
                if ( np.all(np.array(l_seeing) < 2.2)
                        and np.all(np.array(l_ellipt) < 0.3)
                        and np.all(np.array(l_sky) < 1000)
                        and np.all(np.array(l_sources) > 30) ):
                    fields_done.append(myfield)
    return fields_done



if __name__ == "__main__": 
    # Config
    SEEINGLOGS = "seeing-logs/"
    SEEINGLOGS_CSV = 'seeing-logs.csv'
    DONEFILE = 'iphas-fields-done-in-2013.txt'

    # First, parse all the seeing log files
    with open(SEEINGLOGS_CSV, 'w') as output:
        output.write("night,run,field,filter,seeing,ellipt,sky,sources\n")

        for filename in sorted(os.listdir(SEEINGLOGS)):
            fields = parse_log(os.path.join(SEEINGLOGS, filename))
            for myfield in fields:
                output.write(myfield)

    # Using the parsed data, figure out which fields have been completed
    fields_done = interpret_logs(SEEINGLOGS_CSV)
    log.info('Observed {0} IPHAS fields successfully in 2013.'.format(len(fields_done)))
    with open(DONEFILE, 'w') as output:
        output.write('field\n')
        [output.write(myfield+'\n') for myfield in fields_done]
