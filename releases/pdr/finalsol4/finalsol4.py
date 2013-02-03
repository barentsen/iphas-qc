import pyfits

# Load data
qc = pyfits.getdata('../../../qcdata/iphas-qc.fits', 1)
repl = pyfits.getdata('replacements.fits', 1)

def is_finalsol4(field_id):
    """Are we including the given field_id for the Penultimate Data Release (PDR)? """
    c = qc.field('id') == field_id
    # In FINALSOL3?
    if qc.field('is_finalsol3')[c].sum() > 0:
        if field_id in repl.field('id_old') and field_id not in repl.field('id_new'):
            return False # In FINALSOL3 but being replaced
        else:
            return True # In FINALSOL3 and not being replaced
    elif field_id in repl.field('id_new'):
        return True # Not in FINALSOL3 but being replaced

def get_zp_uncorrected(field_id):
    """Returns [zpr, zpi, zph] for a given field"""
    zp = []
    c = qc.field('id') == field_id
    for name in ['zpr', 'zpi', 'zph']:
        zp.append( qc.field('%s' % name)[c][0] )
    return zp

def get_zp_finalsol3(field_id):
    """Returns [zpr_finalsol3, zpi_finalsol3, zph_finalsol3] for a given field"""
    zp = []
    c = qc.field('id') == field_id
    for name in ['zpr_finalsol3', 'zpi_finalsol3', 'zph_finalsol3']:
        zp.append( qc.field('%s' % name)[c][0] )
    return zp

def get_shift_finalsol3(field_id):
    """Returns [zpr_finalsol3, zpi_finalsol3, zph_finalsol3] for a given field"""
    shift = []
    c = qc.field('id') == field_id
    for name in ['zpr', 'zpi', 'zph']:
        shift.append( qc.field('%s_finalsol3' % name)[c][0] - qc.field('%s' % name)[c][0] )
    return shift

def get_zp(field_id):
    """Return the zeropoints for a given field, with shifts applied where necessary"""
    if field_id == '':
        return ['','','']
    
    elif field_id not in repl.field('id_new'):
        # Not being replaced: use FINALSOL3 ZPs
        zp = get_zp_finalsol3(field_id)
    else:
        # Being replaced, use shifted ZPs
        c_repl = repl.field('id_new') == field_id
        # Require at least 20 stars
        if repl.field('n_stars')[c_repl][0] < 20:
            return get_zp_finalsol3(field_id)
        ref_field_id = repl.field('calib_ref')[c_repl][0]
        fsol3_shift = get_shift_finalsol3(ref_field_id)

        zp = get_zp_uncorrected(field_id)
        # Apply shifts  
        # CALIB - NEW = (OLD - NEW) + (CALIB - OLD)     
        zp[0] += ( repl.field('shift_r')[c_repl][0] + fsol3_shift[0] )
        zp[1] += ( repl.field('shift_i')[c_repl][0] + fsol3_shift[1] )
        zp[2] += ( repl.field('shift_h')[c_repl][0] + fsol3_shift[2] )

    return zp


if __name__ == '__main__':

    f = open('finalsol4.csv', 'w')
    f.write('id,is_pdr,zpr_pdr,zpi_pdr,zph_pdr\n')

    for field_id in qc.field('id'):
        is_pdr = is_finalsol4(field_id)
        if not is_pdr:
            f.write('%s,False,,,\n' % (field_id) )
        else:
            zp = '%.3f,%.3f,%.3f' % tuple( get_zp(field_id) )
            f.write('%s,True,%s\n' % (field_id, zp))

    f.close()

