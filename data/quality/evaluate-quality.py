"""
Quality flags A/B/C are assigned to all fields as follows:

 A++: seeing <= 1.25 & ellipt <= 0.20 
      & f_outliers_10p < 0.59 & f_outliers_20p < 0.07
      & {r|i|ha}5sig >= {20.0|19.0|19.0} & rmode >= 18.0
      
 A+ : seeing <= 1.5 & ellipt <= 0.20
      & f_outliers_10p < 1.26 & f_outliers_20p < 0.16
      & {r|i|ha}5sig >= {20.0|19.0|19.0} & rmode >= 18.0

 A  : seeing <= 2.0 & ellipt <= 0.20
      & f_outliers_10p < 4.14 & f_outliers_20p < 0.34
      & {r|i|ha}5sig >= {20.0|19.0|19.0} & rmode >= 18.0
 
 B  : seeing <= 2.5 & ellipt <= 0.20 
      & f_outliers_10p < 4.14 & f_outliers_20p < 0.34
      & {r|i|ha}5sig >= {20.0|19.0|19.0} & rmode >= 18.0

 C  : seeing <= 2.5 & ellipt <= 0.20 
      & f_outliers_10p < 11.6 & f_outliers_20p < 1.06
      & {r|i|ha}5sig >= {20.0|19.0|19.0} & rmode >= 18.0

 D  : all remaining fields (i.e. the worst data.)

Note: the increasing limits for "f_outliers_10p/20p" are based on the 
50/75/90/95%% percentiles of these quality indicators.
"""
import pyfits
import numpy as np


def quality_flag(seeing, ellipt, r5sig, i5sig, h5sig, rmode, f10p, f20p):
    """Returns the quality flag"""
    if (seeing <= 1.25) and (ellipt <= 0.20) \
    and (np.isnan(f10p) or (f10p < 0.59)) \
    and (np.isnan(f20p) or (f20p < 0.07)) \
    and r5sig >= 20.0 and i5sig >= 19.0 and h5sig >= 19.0 and rmode > 17.99:
        return "A++"

    if (seeing <= 1.5) and (ellipt <= 0.20) \
    and (np.isnan(f10p) or (f10p < 1.26)) \
    and (np.isnan(f20p) or (f20p < 0.16)) \
    and r5sig >= 20.0 and i5sig >= 19.0 and h5sig >= 19.0 and rmode > 17.99:
        return "A+"

    if (seeing <= 2.0) and (ellipt <= 0.20) \
    and (np.isnan(f10p) or (f10p < 4.14)) \
    and (np.isnan(f20p) or (f20p < 0.34)) \
    and r5sig >= 20.0 and i5sig >= 19.0 and h5sig >= 19.0 and rmode > 17.99:
        return "A"

    if (seeing <= 2.5) and (ellipt <= 0.20) \
    and (np.isnan(f10p) or (f10p < 4.14)) \
    and (np.isnan(f20p) or (f20p < 0.34)) \
    and r5sig >= 20.0 and i5sig >= 19.0 and h5sig >= 19.0 and rmode > 17.99:
        return "B"

    if (seeing <= 2.5) and (ellipt <= 0.25) \
    and (np.isnan(f10p) or (f10p < 11.6)) \
    and (np.isnan(f20p) or (f20p < 1.06)) \
    and r5sig >= 20.0 and i5sig >= 19.0 and h5sig >= 19.0 and rmode > 17.99:
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


# Evaluate all observations and write the flags
f = open('quality-flags.csv', 'w')
f.write('id,qflag,is_ok\n')

flagcount = {'A++':0, 'A+':0, 'A':0, 'B':0, 'C':0, 'D':0}

for i in range(d.size):
    flag = quality_flag(seeing[i], ellipt[i], r5sig[i], i5sig[i], h5sig[i], rmode[i], f10p[i], f20p[i])
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
