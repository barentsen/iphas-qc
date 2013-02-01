from pylab import *
import pyfits

qc = pyfits.getdata('../../qcdata/iphas-qc.fits', 1)


histprop = {'edgecolor':'black'}


figure() 
myxrange = [0.5, 3]
hist(qc.field('seeing_max'), range=(myxrange[0], myxrange[1]), bins=40, **histprop)
ylabel('N')
xlabel('Seeing (arcsec)')
xlim(myxrange)
savefig('seeing.png', dpi=150)

c_ellipt = qc.field('ellipt_max') > 0.15
hist(qc.field('seeing_max')[c_ellipt], range=(myxrange[0], myxrange[1]), label='Ellipticity > 0.15', bins=40, hatch='/', **histprop)
legend()
savefig('seeing2.png', dpi=150)

"""
c_summer= (qc.field('id').find('jun') > -1) | (qc.field('id').find('jul') > -1) | (qc.field('id').find('aug') > -1) | (qc.field('id').find('sep') > -1)
hist(qc.field('seeing_max'), range=(myxrange[0], myxrange[1]), bins=40, label='Summer (Jun-Sept)', hatch='//', **histprop)

c_winter = (qc.field('id').find('oct') > -1) | (qc.field('id').find('nov') > -1) | (qc.field('id').find('dec') > -1) | (qc.field('id').find('jan') > -1)
hist(qc.field('seeing_max')[c_winter], range=(myxrange[0], myxrange[1]), bins=40, label='Winter (Oct-Jan)', hatch='/', **histprop)


#hist( [qc.field('seeing_max')[c_summer], qc.field('seeing_max')[c_winter]], 
#        range=(myxrange[0], myxrange[1]), bins=40, 
#        label=['Summer (Jun-Sept)', 'Winter (Oct-Jan)'], histtype='bar')

legend()
savefig('seeing_month.png', dpi=150)
"""
close()


figure()
myxrange = [0.0, 0.35] 
hist(qc.field('ellipt_max'), range=(myxrange[0], myxrange[1]), bins=30, **histprop)
ylabel('N')
xlabel('Ellipticity')
xlim(myxrange)
savefig('ellipt.png', dpi=150)

c_2005 = (qc.field('night') > 20050000) & (qc.field('night') < 20060200)
hist(qc.field('ellipt_max')[c_2005], range=(myxrange[0], myxrange[1]), bins=30, label='2005', hatch='/', **histprop)
legend()
savefig('ellipt_2005.png', dpi=150)
close()


figure() 
myxrange = [1.0, 1.6]
hist(qc.field('airmass_max'), range=(myxrange[0], myxrange[1]), bins=40, **histprop)
ylabel('N')
xlabel('Airmass')
xlim(myxrange)
savefig('airmass.png', dpi=150)

c_dec = (qc.field('dec') < 10.)
hist(qc.field('airmass_max')[c_dec], range=(myxrange[0], myxrange[1]), bins=40, label=u'Declination < +10\N{DEGREE SIGN}', hatch='/', **histprop)
legend()
savefig('airmass_dec.png', dpi=150)
close()




for band in ['r', 'h', 'i']:
    figure() 
    myxrange = [18.5, 22.]
    hist(qc.field( band+'5sig_judged'), range=(myxrange[0], myxrange[1]), bins=40, **histprop)
    ylabel('N')
    xlabel(u"5\u03C3-depth in " + band)
    xlim(myxrange)
    savefig('5sig_' + band + '.png', dpi=150)

    c_moon = (qc.field('moon_altitude') > 0.)
    hist(qc.field(band + '5sig_judged')[c_moon], range=(myxrange[0], myxrange[1]), bins=40, label='Moon above horizon', hatch='/', **histprop)
    legend(loc='upper left')
    savefig('5sig_' + band + '_moon.png', dpi=150)

    c_moon_full = (qc.field('moon_phase') > 90.)
    hist(qc.field(band + '5sig_judged')[c_moon_full], range=(myxrange[0], myxrange[1]), bins=40, label='Moon phase > 90%', hatch="//", **histprop)
    legend(loc='upper left')
    savefig('5sig_' + band + '_moon2.png', dpi=150)
    close()



years = np.array([float(str(n)[0:4]) for n in qc.field('night')])
n_bins = 12

figure() 
myxrange = [2001.5, 2013.5]
hist(years, range=(myxrange[0], myxrange[1]), bins=n_bins, **histprop)
ylabel('N')
xlabel("Year")
xlim(myxrange)
savefig('iphas-byyear.png', dpi=150)

c_5sig = (qc.field('r5sig_judged') < 20.5)
hist(years[c_5sig], range=(myxrange[0], myxrange[1]), bins=n_bins, label=u"Depth 5\u03C3(r') < 20.5", hatch='/', **histprop)
legend()
savefig('iphas-byyear2.png', dpi=150)

close()


months = np.array([int(str(n)[4:6]) for n in qc.field('night')])
n_bins = 12

figure() 
myxrange = [0.5, 12.5]
hist(months, range=(myxrange[0], myxrange[1]), bins=n_bins, **histprop)
ylabel('N')
xlabel("Month")
xlim(myxrange)
savefig('iphas-bymonth.png', dpi=150)

c_seeing = (qc.field('seeing_max') > 1.5)
hist(months[c_seeing], range=(myxrange[0], myxrange[1]), bins=n_bins, label='Seeing > 1.5"', hatch='/', **histprop)
legend()
savefig('iphas-bymonth2.png', dpi=150)
close()




n_bins = 50

figure() 
myxrange = [22.0, 225.]
hist(qc.field('l'), range=(myxrange[0], myxrange[1]), bins=n_bins, **histprop)
ylabel('N')
xlabel("Galactic Longitude")
xlim(myxrange)
savefig('l1.png', dpi=150)

c_best = ~qc.field('is_best')
h = hist(qc.field('l')[c_best], range=(myxrange[0], myxrange[1]), bins=n_bins, label="Repeat observations", hatch="/", **histprop)
legend(loc='upper right')
savefig('l2.png', dpi=150)
[p.remove() for p in h[2]]

c_seeing = (qc.field('seeing_max') > 1.5)
h = hist(qc.field('l')[c_seeing], range=(myxrange[0], myxrange[1]), bins=n_bins, label='Seeing > 1.5"', hatch='/', **histprop)
legend(loc='upper right')
savefig('l3.png', dpi=150)
[p.remove() for p in h[2]]

c_5sig = (qc.field('r5sig_judged') < 20.5)
h = hist(qc.field('l')[c_5sig], range=(myxrange[0], myxrange[1]), bins=n_bins, label=u"Depth 5\u03C3(r') < 20.5", hatch="/", **histprop)
legend(loc='upper right')
savefig('l4', dpi=150)
[p.remove() for p in h[2]]

c_moon2 = (qc.field('moon_separation') < 45.)
hist(qc.field('l')[c_moon2], range=(myxrange[0], myxrange[1]), bins=n_bins, label=u"Moon separation < 45\N{DEGREE SIGN}", hatch="/", **histprop)
legend(loc='upper right')
savefig('l5.png', dpi=150)


c_year = (qc.field('dir') == "iphas_aug2003")
hist(qc.field('l')[c_year], range=(myxrange[0], myxrange[1]), bins=n_bins, label="August 2003", hatch="/", facecolor='green', **histprop)
legend(loc='upper right')
savefig('l6.png', dpi=150)


close()




