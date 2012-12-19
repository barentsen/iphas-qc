"""
This script identifies the best data (= month) for each field.

The output is written to a CSV file with one line per field/month
and a boolean indicating whether that data is the best.
"""
import pyfits
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)

# Collated quality information
d = pyfits.getdata('../iphas-observations.fits', 1)

# This dictionary will hold the best data for each field,
# e.g. winners['0001'] = '0001_jul2007'
winners = {'0003': '0003_oct2009', # Field with missing mercat
           '0003o': '0003o_oct2009'}


c_ok = ( (d.field('qflag') == 'A++') | (d.field('qflag') == 'A+') ) | (d.field('qflag') == 'A')

# Loop over all field numbers
for i in range(1, 7636):
    fieldname = "%04d" % i
    # Consider both on- and off-set exposures
    for field in [fieldname, fieldname+"o"]:
        c = ( d.field('field') == field )

        # Skip the loop for fields for which we defined the best field manually
        if winners.has_key(field):
            continue

        if c.sum() > 0: # Has the field been observed at all?

            # If this is an offset field, prefer the month of the on-field
            if field.endswith('o') and winners.has_key(fieldname):
                on_month = winners[fieldname].split('_')[1]
                pairid = field+"_"+on_month
                c_pair = ( d.field('id') == pairid ) & d.field('is_ok')
                if c_pair.sum() > 0:
                    winners[field] = pairid
                    logging.info("%s wins due to partner" % winner_id)
                    continue

            # Good data available?
            #c_ok = d.field('is_ok')[c]
            if c_ok[c].sum() > 0:
                consider = (c & c_ok)
            else:
                cqualb = d.field('qflag')[c] == 'B'
                if cqualb.sum() > 0:
                    consider = c & (d.field('qflag') == 'B')
                else:
                    consider = c

            # Amongst the fields being considered,
            # we choose the one with the faintest r-band 90-percentile
            winner_arg = np.argmax( d.field('rimode2')[consider] )
            winner_id = d.field('id')[consider][winner_arg]
            winners[field] = winner_id

            logging.info("%s wins" % winner_id)



# Write results
out = open('best-fields.csv', 'w')
out.write( "id,is_best\n" )

for i in range(d.size):
    myfield = d.field('field')[i]
    myid = d.field('id')[i]

    if winners.has_key(myfield) and winners[myfield] == myid:
        is_best = "True"
    else:
        is_best = "False"

    out.write( "%s,%s\n" % (myid, is_best) )

out.close()