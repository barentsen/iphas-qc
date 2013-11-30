"""Hack: take out a few fields before releasing the final DR2 data
"""
import numpy as np
from astropy.io import ascii

f = ascii.read('quality.csv')

for field in ascii.read('dr2-embargo.txt'):
    myfield = field[0].strip()
    print myfield
    arg = np.argwhere(f['id'] == myfield)
    print arg
    print f['qflag'][arg]
    f['qflag'][arg] = 'D'
    f['is_ok'][arg] = 'False'
    f['problems'][arg] = 'Embargoed'

f.write('quality-dr2.csv', format='ascii', delimiter=',')

