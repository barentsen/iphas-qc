"""
Converts the IPHAS Quality Control table into JSON format for use in web-interfaces.

"""
import pyfits

qc = pyfits.getdata('../qcdata/iphas-qc.fits', 1)

json = open('iphas-qc.json', 'w')
json.write('var iphasqc = [\n')

for i in range(len(qc)):   
    json.write('{\n');
    json.write('"value":"%s", ' % qc.field('id')[i] )
    
    i_prev = i - 1
    if i_prev < 0:
        i_prev = len(qc)-1
    json.write('"prev":"%s", ' % qc.field('id')[i_prev] )

    i_next = i + 1
    if i_next == len(qc):
        i_next = 0
    json.write('"next":"%s", ' % qc.field('id')[i_next] )

    for col in ['qflag', 'problems']:
        json.write('"%s":"%s", ' % (col, qc.field(col)[i]) )
    json.write('}');
    if i < len(qc)-1:
        json.write(',\n')


json.write('];\n')
json.close()
