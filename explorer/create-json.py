"""
Converts the IPHAS Quality Control table into JSON format for use in web-interfaces.

"""
import pyfits
import numpy as np

qc = pyfits.getdata('../qcdata/iphas-qc.fits', 1)

json = open('iphas-qc.js', 'w')


""" First: simple list of fields """
json.write('var iphas_all = [')
for i in range(len(qc)):
    if i > 0:
        json.write(', ')
    json.write('"%s"' % qc.field('id')[i])
json.write('];\n')

json.write('var iphas_best = [')
for i in range(len(qc)):
    if not qc.field('is_best')[i]:
        continue
    if qc.field('id')[i][0:5] != '0001_':
        json.write(', ')
    json.write('"%s"' % qc.field('id')[i])
json.write('];\n')


json.write('var iphasqc = {\n')

for i in range(len(qc)):
    if i > 0:
        json.write(', \n')
    json.write('"%s": {' % qc.field('id')[i] )
    
    for col in ['ra', 'dec', 'l', 'b']:
        json.write('"%s":"%s", ' % (col, np.round(qc.field(col)[i], 1) ) )
    for col in ['is_best', 'qflag', 'problems']:
        json.write('"%s":"%s", ' % (col, qc.field(col)[i]) )
    
    i_prev = i - 1
    if i_prev < 0:
        i_prev = len(qc)-1
    json.write('"prev":"%s", ' % qc.field('id')[i_prev] )

    i_next = i + 1
    if i_next == len(qc):
        i_next = 0
    json.write('"next":"%s"}' % qc.field('id')[i_next] )


json.write('};\n')
json.close()

