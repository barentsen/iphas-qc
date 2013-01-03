import pyfits
import numpy as np
import time

d = pyfits.getdata('../data/iphas-observations.fits', 1)


is_pdr = d.field('is_pdr')
is_ok = d.field('is_ok')
is_best = d.field('is_best')
fieldid = d.field('id')
field = d.field('field')
qflag = d.field('qflag')
seeing = d.field('seeing_max')
ellipt = d.field('ellipt_max')
r5sig = d.field('r5sig')
i5sig = d.field('i5sig')
h5sig = d.field('h5sig')
rmode = d.field('rmode')
starcount = d.field('n_stars')
n10p = d.field('n_outliers_10p')
n20p = d.field('n_outliers_20p')
f10p = d.field('f_outliers_10p')
f20p = d.field('f_outliers_20p')
sky = d.field('sky_max')
iphasdir = d.field('dir')

pct = [10,25,50,75,90,95,99]
percentiles = np.array([np.percentile( seeing[~np.isnan(seeing)] , pct), 
                        np.percentile( ellipt[~np.isnan(ellipt)] , pct), 
                        np.percentile( r5sig[~np.isnan(r5sig)] , pct), 
                        np.percentile( i5sig[~np.isnan(i5sig)] , pct), 
                        np.percentile( h5sig[~np.isnan(h5sig)] , pct), 
                        np.percentile( rmode[~np.isnan(rmode)] , pct), 
                        np.percentile( n10p[~np.isnan(f10p)] , pct), 
                        np.percentile( n20p[~np.isnan(f20p)] , pct),
                        np.percentile( f10p[~np.isnan(f10p)] , pct),
                        np.percentile( f20p[~np.isnan(f20p)] , pct)])


f = open('iphas-pdr-quality-review.txt', 'w')

is_app = is_pdr & (qflag == "A++")
is_ap = is_pdr & (qflag == "A+")
is_a = is_pdr & (qflag == "A")
is_b = is_pdr & (qflag == "B")
is_c = is_pdr & (qflag == "C")
is_d = is_pdr & (qflag == "D")

f.write(\
"""IPHAS Penultimate Release - data quality review (gb, %s)""" % time.strftime('%Y-%m-%d')
+"""
================================================================

1. Quality classification
-------------------------
Quality flags A/B/C/D are assigned to all fields as follows.
First, all bad fields are automatically classified 'D'.

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


Definition of quality measures:
* f_outliers_10p/f_outliers_20p:
    Fraction of stars showing a shift larger than 10/20%% between the 
    same-month on/off exposures. The increasing limits correspond to 
    the percentiles of the parameter's distributions.
    Serves to detect noise, gain variations and fringing.
* rmode:
    Mode of the r magnitude distribution for those objects which are 
    classified as 'stellar' or 'probably stellar' in both the r/i bands, 
    This measure serves as a proxy for completeness. It is computed using
    a binning of 0.25 mag.
* r5sig/i5sig/h5sig:
    Detection limits in r/i/Ha where SNR = 5 (i.e. where error = 0.20). 
    Serves as a proxy for depth.


Percentiles of quality parameters across all IPHAS observations:
                 10%%   25%%   50%%   75%%   90%%   95%%   99%%
seeing          %.2f  %.2f  %.2f  %.2f  %.2f  %.2f  %.2f
ellipt          %.2f  %.2f  %.2f  %.2f  %.2f  %.2f  %.2f
r5sig           %.1f  %.1f  %.1f  %.1f  %.1f  %.1f  %.1f
i5sig           %.1f  %.1f  %.1f  %.1f  %.1f  %.1f  %.1f
h5sig           %.1f  %.1f  %.1f  %.1f  %.1f  %.1f  %.1f
rmode           %.1f  %.1f  %.1f  %.1f  %.1f  %.1f  %.1f
n_outliers_10p   %3d   %3d   %3d   %3d   %3d   %3d   %3d
n_outliers_20p   %3d   %3d   %3d   %3d   %3d   %3d   %3d
f_outliers_10p  %.2f  %.2f  %.2f  %.2f  %.2f  %.1f  %.1f
f_outliers_20p  %.2f  %.2f  %.2f  %.2f  %.2f  %.2f  %.1f

""" % tuple(percentiles.reshape(percentiles.size,)) )


f.write(\
"""
Breakdown for FINALSOL3.txt (%d fields):
 A++  %d fields
 A+   %d 
 A    %d 
 B    %d 
 C    %d
 D    %d

i.e. we should be unhappy about %d fields (%.0f%%), but there are decent 
replacements for approx 600 fields, which are detailed below.\n\n""" \
% (is_pdr.sum(), is_app.sum(), is_ap.sum(), is_a.sum(), is_b.sum(), is_c.sum(), is_d.sum(), (is_pdr & -is_ok).sum(), (100*(is_pdr & -is_ok).sum() / float(is_pdr.sum())) )  )


f.write( """

2. Replacement fields
---------------------
Based on the quality information in the master table (iphas-observations.fits),
the 'best runs' have been selected as follows. 

Algorithm:
1) For each non-offset field, pre-select all the A-quality runs. If none are 
   available, select B/C/D-quality runs.
2) Select the deepest run amongst those pre-selected in step 1. This is 
   defined as the run with the faintest 'rmode' value.
3) For the offset field, choose the same run as the non-offset field *if* 
   the data is also of A-quality. If the quality is poor or if the offset 
   field was not observed in the same run, then select a different run for 
   the offset field following steps 1+2.

Then, for each field in FINALSOL3.txt where at least one member of the 
fieldpair is of poor quality (B/C/D), an alternative is proposed if an 
A-quality alternative exists. The results are listed below.

# TODO
# * Should we only prefer same-run fields if data was taken in the same night?
# * Prefer a different run if it gives the offset field a superior depth?


field     old   qual/see/ell/f10p/f20p/r5sig/rmode/stars
  =>      new

""")

# First, figure out which fields have flag B or C
c = is_pdr & ~(is_ok | (qflag == 'B') )
needs_replacement = set([])
needs_replacement_list = []
for i, in np.argwhere(c):
    # Consider on/offset fields together
    needs_replacement.add( field[i][0:4] )
    needs_replacement_list.append( field[i] )


def get_pdr_desc(fieldname):
    c = (field == fieldname) & is_pdr
    if c.sum() == 1:
        i = np.argwhere(c)[0][0]
        return "%8s" % iphasdir[i][6:].rjust(8), "%s/%.1f\"/%.2f/%02.0f%%/%02.0f%%/%.1f/%.1f/%02dk" % (qflag[i].rjust(3), seeing[i], ellipt[i], f10p[i], f20p[i], r5sig[i], rmode[i], starcount[i]/1e3)
    return ""

def get_best_desc(fieldname):
    c = (field == fieldname) & is_best
    if c.sum() == 1:
        i = np.argwhere(c)[0][0]
        return "%8s" % iphasdir[i][6:].rjust(8), "%s/%.1f\"/%.2f/%02.0f%%/%02.0f%%/%.1f/%.1f/%02dk" % (qflag[i].rjust(3), seeing[i], ellipt[i], f10p[i], f20p[i], r5sig[i], rmode[i], starcount[i]/1e3)
    return "", ""

no_alternative = []
replacements_count = 0
for fieldname in sorted(needs_replacement):

    replacement = (field == fieldname) & is_best & -is_pdr & is_ok
    fieldname2 = fieldname+"o"
    replacement2 = (field == fieldname2) & is_best & -is_pdr & is_ok

    if ( fieldname not in needs_replacement_list and replacement2.sum() == 0) \
        or (  fieldname2 not in needs_replacement_list and replacement.sum() == 0):
        continue

    if replacement.sum() > 0:
        best_id, best_q = get_best_desc(fieldname)
        pdr_id, pdr_q = get_pdr_desc(fieldname)
        f.write( "%s %s  %18s \n  =>  %s  %18s\n" % (fieldname.ljust(5), pdr_id, pdr_q, best_id, best_q) )
        replacements_count += 1
    #else:
    #    f.write( "%s %s => %s\n" % (fieldname.ljust(5), get_pdr_desc(fieldname).ljust(14), "no improvement") ) 
    
    if replacement2.sum() > 0:
        best_id, best_q = get_best_desc(fieldname2)
        pdr_id, pdr_q = get_pdr_desc(fieldname2)
        f.write( "%s %s  %18s \n  =>  %s  %18s\n" % (fieldname2, pdr_id, pdr_q, best_id, best_q) )
        replacements_count += 1

    if replacement.sum() > 0 or replacement2.sum() > 0:
        f.write("\n")


f.write("\nSummary: found %d candidate replacement fields.\n\nEOF\n" % replacements_count)


f.close()

