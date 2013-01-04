"""
Quality flags A/B/C/D are assigned to all fields as follows.

First, all bad fields are automatically classified 'D':

 D  : ellipt > 0.2 || seeing > 2.5 || rmode < 18 
      || f_outliers_10p > 11.4 || f_outliers_20p > 0.65
      || r5sig < 20 || i5sig < 19 || h5sig < 19

Amongst the remaining fields, cuts are applied to seeing and outliers:

 A++: seeing <= 1.25
      & (n_outliers_10p < 10 || f_outliers_10p < 0.68)
      & (n_outliers_20p < 5  || f_outliers_20p < 0.05)
      
 A+ : seeing <= 1.5
      & (n_outliers_10p < 10 || f_outliers_10p < 1.63)
      & (n_outliers_20p < 5  || f_outliers_20p < 0.14)

 A  : seeing <= 2.0
      & (n_outliers_10p < 10 || f_outliers_10p < 5.02)
      & (n_outliers_20p < 5  || f_outliers_20p < 0.31)

 B  : seeing <= 2.5
      & (n_outliers_10p < 20 || f_outliers_10p < 5.02)
      & (n_outliers_20p < 10 || f_outliers_20p < 0.31)

 C  : seeing <= 2.5
      & (n_outliers_10p < 20 || f_outliers_10p < 11.3)
      & (n_outliers_20p < 10 || f_outliers_20p < 0.65)

Note: the increasing limits for "f_outliers_10p/20p" are based on the 
percentiles of these quality indicators.
"""

import pyfits
import numpy as np


def load_fieldlist(filename):
  """Load a list of fields into a dictionary"""
  fields = [line.split('#')[0].strip() for line in open(filename, 'r').readlines()]
  comments = [line.split('#')[1].strip() for line in open(filename, 'r').readlines()]
  return dict(zip(fields, comments))
 
whitelist = load_fieldlist('whitelist.txt')
blacklist = load_fieldlist('blacklist.txt')


# Load QC data
d = pyfits.getdata('../iphas-qc.fits', 1)
myid = d.field('id')
seeing = d.field('seeing_max')
ellipt = d.field('ellipt_max')
r5sig = d.field('r5sig')
i5sig = d.field('i5sig')
h5sig = d.field('h5sig')
rmode = d.field('rmode')
f10p = d.field('f_outliers_10p')
f20p = d.field('f_outliers_20p')
n10p = d.field('n_outliers_10p')
n20p = d.field('n_outliers_20p')

# Percentiles of crossmatching consistency parameters
pct = [50,75,90,95]
f10p_pct = dict( zip( pct, 
                      np.array( np.percentile(f10p[~np.isnan(f10p)], pct)).round(2) 
                     ) )
f20p_pct = dict( zip( pct, 
                      np.array( np.percentile(f20p[~np.isnan(f20p)], pct)).round(2) 
                     ) )


def quality_flag(fieldid, seeing, ellipt, r5sig, i5sig, h5sig, rmode, f10p, f20p, n10p, n20p):
    """Returns the quality flag"""
    if fieldid in blacklist:
      return "D"

    if r5sig < 20.0 or i5sig < 19.0 or h5sig < 19.0 or rmode < 18.0 or ellipt > 0.2:
      return "D"

    if (seeing <= 1.25) \
    and (fieldid in whitelist or np.isnan(f10p) or (f10p < f10p_pct[50]) or n10p < 20) \
    and (fieldid in whitelist or np.isnan(f20p) or (f20p < f20p_pct[50]) or n20p < 10):
      return "A++"

    if (seeing <= 1.5) \
    and (fieldid in whitelist or np.isnan(f10p) or (f10p < f10p_pct[75]) or n10p < 20) \
    and (fieldid in whitelist or np.isnan(f20p) or (f20p < f20p_pct[75]) or n20p < 10):
        return "A+"

    if (seeing <= 2.0) \
    and (fieldid in whitelist or np.isnan(f10p) or (f10p < f10p_pct[90]) or n10p < 20) \
    and (fieldid in whitelist or np.isnan(f20p) or (f20p < f20p_pct[90]) or n20p < 10):
        return "A"

    if (seeing <= 2.5) \
    and (fieldid in whitelist or np.isnan(f10p) or (f10p < f10p_pct[90]) or n10p < 20) \
    and (fieldid in whitelist or np.isnan(f20p) or (f20p < f20p_pct[90]) or n20p < 10):
        return "B"

    if (seeing <= 2.5) \
    and (fieldid in whitelist or np.isnan(f10p) or (f10p < f10p_pct[95]) or n10p < 20) \
    and (fieldid in whitelist or np.isnan(f20p) or (f20p < f20p_pct[95]) or n20p < 10):
        return "C"

    # else
    return "D"

def quality_problems(fieldid, seeing, ellipt, r5sig, i5sig, h5sig, rmode, f10p, f20p, n10p, n20p):
  """
  Returns a string describing the various quality problems.

  """
  problems = []

  if fieldid in whitelist:
    problems.append( 'whitelisted ('+whitelist[fieldid]+')' )
  if fieldid in blacklist:
    problems.append( 'blacklisted ('+blacklist[fieldid]+')' )

  if r5sig < 20.0:
    problems.append( 'r5sig<20' )
  if i5sig < 19.0:
    problems.append( 'i5sig<19' )
  if h5sig < 19.0:
    problems.append( 'h5sig<19' )
  if rmode < 18.0:
    problems.append( 'rmode<18' )
  if ellipt > 0.2:
    problems.append( 'ellipt>0.2' )

  if seeing > 2.5:
    problems.append( 'seeing>2.5' )
  elif seeing > 2.0:
    problems.append( 'seeing>2' )

  if not np.isnan(f10p) and not np.isnan(f20p):
    if ( (f10p >= f10p_pct[90] and n10p >= 20) 
          or (f20p >= f20p_pct[90] and n20p >= 10) ):
      problems.append( 'outliers' )

  return ' & '.join(problems)



# Evaluate all observations and write the flags
f = open('quality.csv', 'w')
f.write('id,qflag,is_ok,problems\n')

flagcount = {'A++':0, 'A+':0, 'A':0, 'B':0, 'C':0, 'D':0}

for i in range(d.size):
    flag = quality_flag(myid[i], seeing[i], ellipt[i], 
                        r5sig[i], i5sig[i], h5sig[i], rmode[i], 
                        f10p[i], f20p[i], n10p[i], n20p[i])
    problems = quality_problems(myid[i], seeing[i], ellipt[i], 
                        r5sig[i], i5sig[i], h5sig[i], rmode[i], 
                        f10p[i], f20p[i], n10p[i], n20p[i])
    flagcount[flag] += 1
    # Quality acceptable?
    if flag.startswith('A') or flag.startswith('B') or flag.startswith('C'):
        is_quality_ok = "True"
    else:
        is_quality_ok = "False"
    f.write( "%s,%s,%s,%s\n" % (myid[i], flag, is_quality_ok, problems) )

f.close()


# Write some debugging output
print "f10p percentiles: %s" % f10p_pct
print "f20p percentiles: %s" % f20p_pct
print "Fields per flag:"
print flagcount
