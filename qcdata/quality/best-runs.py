"""
This script identifies the best run for each field.

The output is written to a CSV file with one line per field/month
and a boolean indicating whether that data is the best.

Terminology
===========
* field: a pointing in the sky;
* run: epoch at which a certain field was observed.
"""
import pyfits
import numpy as np

# Collated quality information
qc = pyfits.getdata('../iphas-qc.fits', 1)


""" HELPER FUNCTIONS """

def get_runs(fieldname):
    """
    Returns a list of all runs for a field

    """
    c = (qc.field('field') == fieldname)
    dirs = np.unique( qc.field('dir')[c] )
    return dirs

def get_runs_by_flag(fieldname):
    """
    Returns a list of all runs for a field,
    organized in a dictionary indexed by quality flag.

    """
    runs =  get_runs(fieldname)
    grades = {'A':[], 'B':[], 'C':[], 'D':[]}
    for run in runs:
        mygrade = get_qflag(fieldname, run)[0:1]
        grades[mygrade].append( run )
    return grades

def get_fieldpair_runs(fieldname):
    """ 
    Returns a list of runs for all fieldpairs

    fieldname (string): name of the on field (e.g. "0001")
    """
    c_on = (qc.field('field') == fieldname) 
    c_off = (qc.field('field') == fieldname+'o')
    dirs = np.unique(qc.field('dir')[c_on])
    
    result = []
    for mydir in dirs:
        c_dir = qc.field('dir') == mydir
        if (c_on & c_dir).sum() == 1 & (c_off & c_dir).sum() == 1:
            # Only select pairs!
            result.append( mydir )
    return result

def get_fieldpair_runs_by_flag(fieldname):
    runs =  get_fieldpair_runs(fieldname)
    # What is the lowest grade for each fieldpair?
    grades = {'A':[], 'B':[], 'C':[], 'D':[]}
    for run in runs:
        mygrade = worst_grade(fieldname, run)
        grades[mygrade].append( run )
    return grades

def get_id(fieldname, run):
    """
    ID of a field/run combination

    """
    if run == None:
        return None
    c_dir = qc.field('dir') == run
    c = c_dir & (qc.field('field') == fieldname) 
    return qc.field('id')[c][0]

def get_qflag(fieldname, run):
    """
    Quality flag of a single field/run combination

    """
    if run == None:
        return None
    c_dir = qc.field('dir') == run
    c = c_dir & (qc.field('field') == fieldname)
    if c.sum() > 0:
        return qc.field('qflag')[c][0]
    else:
        return None

def get_rmedian(fieldname, run):
    """
    Get the rmedian (proxy for completeness) for a given field/run combination

    """
    c_dir = qc.field('dir') == run
    c = c_dir & (qc.field('field') == fieldname) 
    return qc.field('rmedian_judged')[c][0]

def worst_grade(fieldname, run):
    """
    Returns the lowest grade amongst the two partners in a fieldpair

    """
    flag1 = get_qflag(fieldname, run)
    flag2 = get_qflag(fieldname+'o', run)

    for flag in ['D', 'C', 'B', 'A']:
        if flag1.startswith(flag) or flag2.startswith(flag):
            return flag

def best_run_fieldpair(fieldname):
    """
    Returns the best fieldpair if one exists, otherwise return 'None'

    """
    # Get a dictionary of runs for the given fieldpair, indexed by quality
    grades = get_fieldpair_runs_by_flag(fieldname)
    if len(grades['A']) == 0:
        # Only return a winner if a fieldpair exist with both partners of A-quality
        return None
    elif len(grades['A']) == 1:
        # We have one winner
        return grades['A'][0]
    else:
        # We have multiple good candidates, 
        #choose the one with the best mean rmedian
        means = []
        for run in grades['A']:
            rmedian_mean = ( get_rmedian(fieldname, run) 
                           + get_rmedian(fieldname+'o', run) ) / 2.0
            means.append( rmedian_mean )
        return grades['A'][ np.argmax(means) ]

def deepest_amongst_runs(fieldname, runs):
    """
    Amongst a set of runs for a given field,
    choose the one with the best rmedian

    """
    medians = []
    for run in runs:
        medians.append( get_rmedian(fieldname, run) )
    return runs[ np.argmax(medians) ]


def best_run(fieldname):
    runs = get_runs_by_flag(fieldname)
    for flag in ['A', 'B', 'C', 'D']:
        if len(runs[flag]) > 0:
            return deepest_amongst_runs(fieldname, runs[flag])
    # Else
    return None

def best_ids(fieldname):
    best = best_run_fieldpair(fieldname)
    if best != None:
        id1 = get_id(fieldname, best)
        id2 = get_id(fieldname+'o', best)
        return id1, id2
    else:
        run1 = best_run(fieldname)
        id1 = get_id(fieldname, run1)

        # For the partner, give preference to same-epoch if A-quality
        qflag2 = get_qflag(fieldname+'o', run1)
        if qflag2 != None and qflag2.startswith('A'):
            id2 = get_id(fieldname+'o', run1)
        else:
            id2 = get_id(fieldname+'o', best_run(fieldname+'o') )

        return id1, id2


if __name__ == '__main__':
    # The algorithm can be overriden by specifying winners manually
    #override = {'0003': ['0003_oct2009', '0003o_oct2009'] } # Good field, but mercat missing
    override = {}

    # First, figure out the best run for each field
    winners = []
    for i in range(1, 7636):
        fieldname = "%04d" % i
        if fieldname in override:
            id1, id2 = override[fieldname]
        else:
            id1, id2 = best_ids(fieldname)
        winners.append( id1 )
        winners.append( id2 )

    # Then, write our findings to csv with one line per observation
    out = open('best-runs.csv', 'w')
    out.write('id,is_best\n')
    for myid in qc.field('id'):
        if myid in winners:
            is_best = True
        else:
            is_best = False
        out.write('%s,%s\n' % (myid, is_best) )
    out.close()
