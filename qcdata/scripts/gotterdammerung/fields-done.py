"""Transforms get_seeing.perl logs into a list of IPHAS fields truly done"""
import pyfits
import numpy as np

d = pyfits.getdata('seeing.fits', 1)


current_field = ""

for i in range(len(d)):

	if d.field('field')[i].startswith('intphas'):
		myfield = d.field('field')[i].split('_')[1]

		if myfield != current_field:
			current_field = myfield
			l_filters, l_seeing, l_ellipt, l_sky, l_sources = [], [], [], [], []
		
		l_filters.append( d.field('filter')[i] )
		l_seeing.append( d.field('seeing')[i] )
		l_ellipt.append( d.field('ellipt')[i] )
		l_sky.append( d.field('sky')[i] )
		l_sources.append( d.field('sources')[i] )

		if len(l_filters) == 3 and l_filters == ['Ha', 'r', 'i']:
			# Does the observation statisfy the quality constraints?
			if ( np.all(np.array(l_seeing) < 1.8)
					and np.all(np.array(l_ellipt) < 1.2)
					and np.all(np.array(l_sky) < 400)
					and np.all(np.array(l_sources) > 100) ):
				print myfield

	