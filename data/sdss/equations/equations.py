import pyfits
import numpy as np
from pylab import *
interactive(False)

results = open('results.txt', 'w')


def report(line):
    """Print a message to stdout + results file"""
    print line
    results.write(line+"\n")


def sigmaclip_fit(x, y, sigma, iterations):
    use = np.array([True]*len(x))

    for i in range(iterations):
        fit = polyfit(x[use], y[use], 1)
        myfunc = np.poly1d(fit)
        delta = myfunc(x) - y
        sd = np.std(delta[use])
        use = use & ( abs(delta) < (iterations-i)*sigma*sd )

        report("Sigma-clipping iteration %d" % i)
        report( "y = %+.3f x %+.3f" % (fit[0], fit[1]) )
        report( "1-sigma error = %.2f" % sd )

    return fit


def plot_contours(axes, xdata, ydata, myxlim, myylim):
    H, xedges, yedges = np.histogram2d(xdata, ydata, range=[myxlim, myylim], bins=(100, 100))
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

    m = H.max()

    levels = ((0.8/8.)*m, (0.8/4.)*m, (0.8/2.)*m, 0.8*m, m)
    cset = axes.contourf(transpose(H), levels, origin='lower', \
                colors=['#cccccc', '#999999', '#666666', '#333333'], extent=extent)
    cset = axes.contour(transpose(H), levels, origin='lower', \
                colors=['black'],
                linewidths=(1.0),
                linestyles='solid',
                extent=extent)

    xlim(myxlim)
    ylim(myylim)




"""GET DATA"""

d = pyfits.getdata('iphas-x-sdss-for-anchors.fits', 1)

# Remove extreme outliers
# Don't trust g magnitudes fainter than 22


outliers = ((d.field('iphas_i')-d.field('sdss_i')) < -0.5) \
        | ((d.field('iphas_i')-d.field('sdss_i')) > 0.0) \
        | ((d.field('sdss_r')-d.field('sdss_i')) < 0.0)

use = (d.field('anchor') == 1) & (d.field('sdss_g') < 22) #& (-outliers)
iphas_i = d.field('iphas_i')[use]
iphas_r = d.field('iphas_r')[use]
sdss_r = d.field('sdss_r')[use]
sdss_g = d.field('sdss_g')[use]
sdss_i = d.field('sdss_i')[use]


"""PREPARE PLOT"""
figure(figsize=(8,8))
subplots_adjust(0.12,0.1,0.95,0.9)


""" r BAND """
report("\nr band\n============")
ax = subplot(211)

xdata = sdss_g - sdss_r
ydata = iphas_r - sdss_r
plot_contours(ax, xdata, ydata, [-0.1, 2.6], [-0.35, 0.35])

# Fit
fit = sigmaclip_fit(xdata, ydata, 0.5, 30)
transform = np.poly1d(fit)
xp = linspace(-0.5, 3, 10)
ax.plot(xp, transform(xp), c='red', lw=2)

report( "\nr_{IPHAS}[Vega] = r_{SDSS} %+.3f %+.3f (g_{SDSS} - r_{SDSS})" % (fit[1], fit[0]) )
report( "No clipping 1-sigma error = %.2f" % ( std(ydata - transform(xdata)) ) )

ylabel('$\mathrm{r_{IPHAS}\ [Vega]\ -\ r_{SDSS}\ [AB]}$')
xlabel('$\mathrm{g_{SDSS}-r_{SDSS}\ [AB]}$')


""" i BAND """
report("\ni band\n============")

ax = subplot(212)

xdata = sdss_r - sdss_i
ydata = iphas_i - sdss_i
plot_contours(ax, xdata, ydata, [-0.1, 1.3], [-0.65, 0.15])

# Fit
fit = sigmaclip_fit(xdata, ydata, 0.5, 30)
transform = np.poly1d(fit)
ax.plot(xp, transform(xp), c='red', lw=2)

report( "\ni_{IPHAS}[Vega] = i_{SDSS} %+.3f %+.3f (r_{SDSS} - i_{SDSS})" % (fit[1], fit[0]) )
report( "No clipping 1-sigma error = %.2f" % ( std(ydata - transform(xdata)) ) )

ylabel('$\mathrm{i_{IPHAS}\ [Vega]\ -\ i_{SDSS}\ [AB]}$')
xlabel('$\mathrm{r_{SDSS}-i_{SDSS}\ [AB]}$')

savefig('equations.png')

close()

results.close()