"""
Quality flags A/B/C/D are assigned to all fields as follows.

First, all bad fields are automatically classified 'D':

 D  : ellipt > 0.2 || seeing > 2.5 || rmode < 18 
      || f_outliers_10p > 11.4 || f_outliers_20p > 0.65
      || r5sig < 20 || i5sig < 19 || h5sig < 19

Amongst the remaining fields, cuts are applied to seeing and outliers:

 A++: seeing <= 1.25
      & (n_outliers_10p < 10 || f_outliers_10p < 0.65)
      & (n_outliers_20p < 5  || f_outliers_20p < 0.04)
      
 A+ : seeing <= 1.5
      & (n_outliers_10p < 10 || f_outliers_10p < 1.58)
      & (n_outliers_20p < 5  || f_outliers_20p < 0.13)

 A  : seeing <= 2.0
      & (n_outliers_10p < 10 || f_outliers_10p < 5.10)
      & (n_outliers_20p < 5  || f_outliers_20p < 0.28)

 B  : seeing <= 2.5
      & (n_outliers_10p < 20 || f_outliers_10p < 5.11)
      & (n_outliers_20p < 10 || f_outliers_20p < 0.28)

 C  : seeing <= 2.5
      & (n_outliers_10p < 20 || f_outliers_10p < 11.4)
      & (n_outliers_20p < 10 || f_outliers_20p < 0.64)

Note: the increasing limits for "f_outliers_10p/20p" are based on the 
percentiles of these quality indicators.
"""
import pyfits
import numpy as np

# Fields whose f_outliers measure should be ignored
#whitelist = []
whitelist = ['6219_oct2003', '6219o_oct2003'] # E-mail Janet 20121220


def quality_flag(fieldid, seeing, ellipt, r5sig, i5sig, h5sig, rmode, f10p, f20p, n10p, n20p):
    """Returns the quality flag"""
    if r5sig < 20.0 or i5sig < 19.0 or h5sig < 19.0 or rmode < 18.0 or ellipt > 0.2:
      return "D"

    if (seeing <= 1.25) \
    and (fieldid in whitelist or np.isnan(f10p) or (f10p < 0.65) or n10p < 10) \
    and (fieldid in whitelist or np.isnan(f20p) or (f20p < 0.04) or n20p < 5):
      return "A++"

    if (seeing <= 1.5) \
    and (fieldid in whitelist or np.isnan(f10p) or (f10p < 1.58) or n10p < 10) \
    and (fieldid in whitelist or np.isnan(f20p) or (f20p < 0.13) or n20p < 5):
        return "A+"

    if (seeing <= 2.0) \
    and (fieldid in whitelist or np.isnan(f10p) or (f10p < 5.11) or n10p < 10) \
    and (fieldid in whitelist or np.isnan(f20p) or (f20p < 0.28) or n20p < 5):
        return "A"

    if (seeing <= 2.5) \
    and (fieldid in whitelist or np.isnan(f10p) or (f10p < 5.11) or n10p < 20) \
    and (fieldid in whitelist or np.isnan(f20p) or (f20p < 0.28) or n20p < 10):
        return "B"

    if (seeing <= 2.5) \
    and (fieldid in whitelist or np.isnan(f10p) or (f10p < 11.4) or n10p < 20) \
    and (fieldid in whitelist or np.isnan(f20p) or (f20p < 0.64) or n20p < 10):
        return "C"

    # else
    return "D"


# Load quality data
d = pyfits.getdata('../iphas-observations.fits', 1)
myid = d.field('id')

seeing = d.field('seeing_max')
ellipt = d.field('ellipt_max')
r5sig = d.field('r5sig')
i5sig = d.field('i5sig')
h5sig = d.field('h5sig')
#rmode = d.field('rmode')
rmode = d.field('rimode2')
f10p = d.field('f_outliers_10p')
f20p = d.field('f_outliers_20p')
n10p = d.field('n_outliers_10p')
n20p = d.field('n_outliers_20p')


# Evaluate all observations and write the flags
f = open('quality-flags.csv', 'w')
f.write('id,qflag,is_ok\n')

flagcount = {'A++':0, 'A+':0, 'A':0, 'B':0, 'C':0, 'D':0}

for i in range(d.size):
    flag = quality_flag(myid[i], seeing[i], ellipt[i], r5sig[i], i5sig[i], h5sig[i], rmode[i], f10p[i], f20p[i], n10p[i], n20p[i])
    flagcount[flag] += 1
    # Quality acceptable?
    if flag.startswith('A') or flag.startswith('B') or flag.startswith('C'):
        is_quality_ok = "True"
    else:
        is_quality_ok = "False"
    f.write( "%s,%s,%s\n" % (myid[i], flag, is_quality_ok) )

f.close()

print "Result:"
print flagcount
