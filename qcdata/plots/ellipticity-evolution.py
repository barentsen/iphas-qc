from pylab import *
import numpy as np
import pyfits

#d = pyfits.getdata("../mikes-dqc-data.fits", 1)
d = pyfits.getdata("../mikes-dqc-data-iphas-and-uvex.fits", 1)


#for t in d.time:
#	print t
#	datetime.datetime.strptime(t[0:16], "%Y-%m-%d %H:%M")

t = np.array([datetime.datetime.strptime(t[0:10], "%Y-%m-%d") for t in d.time])

years = range(2003,2011) + [2012]
fractions, n_bad, n_all = [], [], []

for myyear in years:
	begin = datetime.datetime(myyear, 1, 1)
	end = datetime.datetime(myyear+1, 1, 1)
	mask = (t > begin) & (t < end)

	el = d.ellipt[mask]
	my_n_bad = len(el[el > 0.2])
	my_n_all = len(el)
	myfraction = my_n_bad / float(my_n_all)

	n_bad.append( my_n_bad )
	n_all.append( my_n_all )
	fractions.append( myfraction )


for varname in ["years", "n_bad", "n_all", "fractions"]:
	vars()[varname] = np.array(vars()[varname])


figure()
title("Fraction of IPHAS/UVEX exposures with ellipticity > 0.2", fontsize=24)
xlabel("Year", fontsize=22)
ylabel("Fraction [%]", fontsize=22)
#scatter(t, d.ellipt)
scatter(years, fractions*100, s=60)

for i, myyear in enumerate(years):
	offset = 0.45
	if myyear == 2007:
		offset = -0.2
	text(myyear, fractions[i]*100-offset, "%s/%s" % (n_bad[i], n_all[i]), \
		horizontalalignment="center")

ax = axes()
ax.title.set_y(1.02) # Push title up
loc = matplotlib.ticker.FixedLocator(years)
ax.xaxis.set_major_locator(loc)


xlim([2002,2013])
#ylim([0,8])
savefig("iphas-uvex-ellipticity-evolution.png", dpi=120)
show()