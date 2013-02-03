"""
List replacements for D-graded or missing fields in the PDR

"""
import pyfits
import numpy as np
from pylab import *

qc = pyfits.getdata('../../qcdata/iphas-qc.fits', 1)


def get_finalsol3(field):
    """Returns the information for the FINALSOL3-run of a given field"""
    c_finalsol3 = (qc.field('field') == field) & qc.field('is_finalsol3')
    n_finalsol3 = c_finalsol3.sum()
    assert(n_finalsol3 <= 1)
    if n_finalsol3 == 1:
        return {'id': qc.field('id')[c_finalsol3][0],
                'qflag': qc.field('qflag')[c_finalsol3][0],
                'is_ok': qc.field('is_ok')[c_finalsol3][0],
                'problems': qc.field('problems')[c_finalsol3][0],
                'rmedian': qc.field('rmedian')[c_finalsol3][0],
                'n_stars': qc.field('n_stars')[c_finalsol3][0]
                }
    else:
        return None

def get_best(field):
    """Returns the information for the best run of a given field"""
    c_best = (qc.field('field') == field) & qc.field('is_best')
    n_best = c_best.sum()
    assert(n_best <= 1)
    if n_best == 1:
        return {'id': qc.field('id')[c_best][0],
                'field': qc.field('field')[c_best][0],
                'qflag': qc.field('qflag')[c_best][0],
                'is_ok': qc.field('is_ok')[c_best][0],
                'l': qc.field('l')[c_best][0],
                'b': qc.field('b')[c_best][0],
                'problems': qc.field('problems')[c_best][0],
                'rmedian': qc.field('rmedian')[c_best][0],
                'n_stars': qc.field('n_stars')[c_best][0]
                }
    else:
        return None


def get_calib(fieldid):
    result = {}
    columns = ['zpr', 'zpi', 'zph', 
                'zpr_finalsol3', 'zpi_finalsol3', 'zph_finalsol3',
                'apass_r', 'apass_i', 
                'sdss_r', 'sdss_i']
    c_id = (qc.field('id') == fieldid) 
    if c_id.sum() == 0:
        for col in columns:
            result[col] = np.nan
        return result
    else:
        for col in columns:
            result[col] = qc.field(col)[c_id][0]
        return result


def calib_shift(id1, id2):
    """Computes calibration shifts"""
    reference_columns = ['apass_r', 'apass_i', 'sdss_r', 'sdss_i']
    result = {}

    calib1 = get_calib(id1)
    calib2 = get_calib(id2)
    
    for col in reference_columns:
        result[col] = calib1[col] - calib2[col]

    return result


def calib(id1, id2):
    if id1 == "":
        return None

def print_status():
    is_finalsol3 = qc.field('is_finalsol3')
    qflag = qc.field('qflag')
    is_finalsol3_d = is_finalsol3 & (qflag == 'D')
    print 'FINALSOL3 has %s fields (i.e. missing %s)' % (
                is_finalsol3.sum(), 
                7635*2-is_finalsol3.sum() )
    print '%s are D-graded' % is_finalsol3_d.sum()


def calib_ref(old, new):
    # A previous run in FINALSOL3 existed
    if old['id'] != '':
        return old['id']
    # Else find a nearby alternative
    c_id = (qc.field('id') == new['id'])
    l, b = qc.field('l')[c_id][0], qc.field('b')[c_id][0]

    c_ref = ( qc.field('is_finalsol3') 
              & qc.field('is_ok')
              & ~c_id
              & ( np.abs(qc.field('l')-l) < 0.5 )
              & ( np.abs(qc.field('b')-b) < 0.5 ) )

    d = np.sqrt(np.abs(qc.field('l')[c_ref]-l)**2 + np.abs(qc.field('b')[c_ref]-b)**2)
    winner = argmin(d)
    return qc.field('id')[c_ref][winner]



print_status()

l, b = [], []

out = open('replacements.csv', 'w')
out.write('field,id_old,id_new,qflag_old,qflag_new,problems_old,problems_new,rmedian_old,rmedian_new,nstars_old,nstars_new,l,b,shift_sdss_r,shift_sdss_i,shift_apass_r,shift_apass_i,calib_ref\n')
""" Missing fields """
for fieldno in range(1, 7635+1):
    field = '%04d' % fieldno

    old1 = get_finalsol3( field )
    old2 = get_finalsol3( field+'o' )

    if ( old1 == None or old1['qflag'] == 'D'
         or old2 == None or old2['qflag'] == 'D'):
        new1 = get_best(field)
        new2 = get_best(field+'o')

        if (new1 != None and new1['is_ok']
            and new2 != None and new2['is_ok'] ):

            if old1 == None: old1 = {'id':'', 'qflag':'', 'problems':'Was missing', 'rmedian':'', 'n_stars':''}
            if old2 == None: old2 = {'id':'', 'qflag':'', 'problems':'Was missing', 'rmedian':'', 'n_stars':''}

            calib1 = calib_shift(old1['id'], new1['id'])
            calib2 = calib_shift(old2['id'], new2['id'])

            ref1 = calib_ref(old1, new1)
            ref2 = calib_ref(old2, new2)

            out.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
                        new1['field'],
                        old1['id'], new1['id'], 
                        old1['qflag'], new1['qflag'],
                        old1['problems'], new1['problems'],
                        old1['rmedian'], new1['rmedian'],
                        old1['n_stars'], new1['n_stars'],
                        new1['l'], new1['b'],
                        calib1['sdss_r'], calib1['sdss_i'],
                        calib1['apass_r'], calib1['apass_i'], 
                        ref1))
            out.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
                        new2['field'],
                        old2['id'], new2['id'], 
                        old2['qflag'], new2['qflag'],
                        old2['problems'], new2['problems'],
                        old2['rmedian'], new2['rmedian'],
                        old2['n_stars'], new2['n_stars'],
                        new2['l'], new2['b'],
                        calib2['sdss_r'], calib2['sdss_i'],
                        calib2['apass_r'], calib2['apass_i'], 
                        ref2))

            l.append( new1['l'] )
            l.append( new2['l'] )
            b.append( new1['b'] )
            b.append( new2['b'] )

out.close()
print 'Found %d replacements' % (len(l))

"""Make a simple overview plot"""
figure(figsize=(12,4.5))
scatter(l, b, marker='x', lw=1, label='Replacements')
#scatter(l_new, b_new, marker='+', lw=1, edgecolor='red', label='Additions')
grid()
xlabel('l')
ylabel('b')
xlim([25,225])
ylim([-5.5,+5.5])
title('FINALSOL3 changes')
savefig('replacements.png')
close()
