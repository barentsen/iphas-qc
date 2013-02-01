from pylab import *
import pyfits

qc = pyfits.getdata('../../qcdata/iphas-qc.fits', 1)


figure()
colors = ['#1A9850', '#91CF60', '#D9EF8B', '#FEE08B', '#FC8D59', '#D73027']
flags = ['A++', 'A+', 'A', 'B', 'C', 'D']
for i, f in enumerate(flags):
    c = qc.field('is_best') & (qc.field('qflag') == f)
    n = c.sum()
    bar(i+0.6, n, width=0.8, facecolor=colors[i], edgecolor='black')

xticks(arange(6)+1, flags, fontsize=36)

#hist(flagno, range=(0.5,6.5), bins=6, rwidth=0.5, )
xlim([0,7])

#xlabel('Quality flag')
#ylabel('N')

savefig('flags.png', dpi=150)

close()