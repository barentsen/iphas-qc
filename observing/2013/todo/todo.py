#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create IPHAS observation todo lists.

Priorities
A: missing from DR2
B: poor seeing or depth in DR2 or serious scattered light problem 
C: mild scattered light problems
"""                                                 
from __future__ import division, print_function, unicode_literals 
import re
import os
import numpy as np
from astropy.io import fits
from astropy.io import ascii
from astropy import log

IPHASQC = fits.getdata('/home/gb/dev/iphas-qc/qcdata/iphas-qc.fits', 1)
FIELDS_DONE = ascii.read('../done/iphas-fields-done-in-2013.txt', 'r')['field']
RA_BINS = [18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7]


##########
# CLASSES
##########

class IPHASToDo(object):

    def __init__(self):
        # Create data structure to hold todo lists, grouped by RA bin
        self.todo = {}
        for ra in RA_BINS:
            self.todo[ra] = []
        # Another dictionary to keep track of the bin a field has been put in
        self.track_assignments = {}
        # Load the definitions of fields
        fieldinfo = open('../../fields.txt', 'r').readlines()
        self.definitions = dict(zip(
                                    [m.split(' ')[0].split('_')[1] 
                                    for m in fieldinfo], 
                                    fieldinfo
                            ))

    def add_fields(self, fieldlist):
        """Add a list of field names to the todo list."""
        for field in fieldlist:
            self.add_field(field)

    def add_field(self, fieldname):
        """Add a single fieldname to the todo list."""
        fielddef = self.definitions[fieldname]
        # Make sure we put fieldpairs in the same bin
        if self.track_assignments.has_key(fieldname[0:4]):
            ra = self.track_assignments[fieldname[0:4]]
        else:
            ra = int(re.split("\W+", fielddef)[1])
            self.track_assignments[fieldname[0:4]] = ra
        # Avoid duplicates
        if (not (fieldname in FIELDS_DONE) and
            not (fielddef in self.todo[ra])):
            self.todo[ra].append(fielddef)

    def print_stats(self):
        n_total = len(np.concatenate([self.todo[ra] for ra in RA_BINS]))
        print('Total: {0} unique fields'.format(n_total))
        # Print number of fields per bin
        for ra in RA_BINS:
            print('{0:02d}h: {1}'.format(ra, len(self.todo[ra])))


    def write_todo_files(self, directory='output'):
        """Write the todo lists to disk."""
        for ra in RA_BINS:
            filename = os.path.join(directory,
                                   'fields.todo.{0:02d}h'.format(ra))
            with open(filename, 'w') as output:
                for myfield in self.todo[ra]:
                    output.write(myfield)

    def write_done_file(self, directory='output'):
        """Writes the fields.done file, listing all fields not to observe."""
        all_fields_todo = np.concatenate([self.todo[ra] for ra in RA_BINS])
        filename = os.path.join(directory, 'fields.done')
        with open(filename, 'w') as output:
            for fieldnumber in np.arange(1, 7635+0.1, 1, dtype=int):
                fieldnumber = '{0:04d}'.format(fieldnumber)
                for field in [fieldnumber, fieldnumber+'o']:
                    fielddef = self.definitions[field]
                    if fielddef not in all_fields_todo:
                        output.write(fielddef)

    def test_output(self, directory='output'):
        """Raises an exception if the output looks invalid."""
        # Count total number of fields todo
        n_todo = 0
        for ra in RA_BINS:
            filename = os.path.join(directory, 'fields.todo.{0:02d}h'.format(ra))
            n_todo += len(open(filename, 'r').readlines())
        # Count total number of fields done
        filename_done = os.path.join(directory, 'fields.done'.format(ra))
        n_done = len(open(filename_done, 'r').readlines())
        # Their sum should be the total number of fields
        assert((n_done+n_todo) == 15270)



###########
# FUNCTIONS
###########

def priority_a():
    """Returns a list of fields to be repeated with the highest priority"""
    fields = []
    # Check all fields on their presence in DR2
    for fieldnumber in np.arange(1, 7635+0.1, 1, dtype=int):
        fieldnumber = '{0:04d}'.format(fieldnumber)
        for field in [fieldnumber, fieldnumber+'o']:
            idx_field = np.where(IPHASQC['is_dr2'] & (IPHASQC['field'] == field))
            if (len(idx_field) > 0) and IPHASQC['qflag'][idx_field].startswith('A'):
                # Pass
                pass
            else:
                fields.append(field)
    log.info('Identified {0} priority A fields'.format(len(fields)))
    return fields

def priority_b():
    """Returns a list of field to be repeated with the second highest priority"""
    fields = []
    mask_priority_b = ( IPHASQC['is_dr2'] & 
                        (IPHASQC['l'] < 90) &
                           (
                                (IPHASQC['seeing_max'] >= 1.8) |
                                (IPHASQC['r5sig_judged'] < 20.0)
                            )
                      )
    for idx in np.where(mask_priority_b)[0]:
        fields.append(IPHASQC['field'][idx])
    log.info('Identified {0} priority B fields'.format(len(fields)))
    return fields

def scattered_light():
    """Returns a list of fields badly affected by scattered light."""
    with open('dr2-scattered-light.txt', 'r') as myfile:
        fields = [row.strip().split('_')[0] for row in myfile.readlines()]
        return fields


########
# MAIN
########
if __name__ == "__main__": 
    
    todo = IPHASToDo()
    todo.add_fields(priority_a())
    todo.add_fields(scattered_light())
    todo.add_fields(priority_b())
    todo.print_stats()
    todo.write_todo_files()
    todo.write_done_file()
    todo.test_output()
    
