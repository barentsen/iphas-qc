"""
Compute the distance and illumation fraction of the moon
for all IPHAS exposures

"""
import pyfits
import ephem
import math as m

def sphere_distance(equ1, equ2):
    """
    Returns the great-circle distance between two points on a sphere,
    using the "Haversine" formula. 

    Input:
    equ1: [x,y] spherical coordinates in degrees (e.g. [ra,dec] or [lon,lat])
    equ2: [x,y] spherical coordinates in degrees
    
    Output:
    great-circle distance between equ1 and equ2 in degrees (float)
    
    Tests:
    >>> sphere_distance([0.0,0.0], [0.0,0.0])
    0.0
    >>> sphere_distance([0.0,0.0], [90.0,0.0])
    90.0
    >>> sphere_distance([0.0,90.0], [90.0,0.0])
    90.0
    """ 
    d_lon = equ2[0] - equ1[0]
    d_lat = equ2[1] - equ1[1]
        
    a = m.sin(m.radians(d_lat)/2.0)**2.0 + m.cos(m.radians(equ1[1])) * m.cos(m.radians(equ2[1])) * m.sin(m.radians(d_lon)/2.0)**2.0
    result = 2.0 * m.atan2(m.sqrt(a), m.sqrt(1.0-a))
    return m.degrees(result)

# Coordinates for the Isaac Newton Telescope
# taken from http://www.ing.iac.es/Astronomy/telescopes/int/
telescope = ephem.Observer()
telescope.lon = '-17.878'
telescope.lat = '+28.762'
telescope.elevation = 2336.0


out = open('moon.csv', 'w')
out.write('id,time,moon_altitude,moon_separation,moon_phase\n')

# Loop over all fields
d = pyfits.getdata('../iphas-observations.fits', 1)
for i in range(d.size):
    mytime = d.field('time_r')[i]
    if mytime == '':
        continue

    telescope.date = mytime.replace("-", "/").replace("T", " ")

    moon = ephem.Moon(telescope)

    # Distance between exposure and moon
    field_equ = [d.field('ra')[i], d.field('dec')[i]]
    moon_equ = [m.degrees(moon.ra), m.degrees(moon.dec)]
    moon_separation = sphere_distance(field_equ, moon_equ)

    out.write('%s,%s,%.1f,%.1f,%.1f\n' % ( d.field('id')[i],
                                       mytime,
                                       m.degrees(moon.alt),
                                       moon_separation,
                                       moon.phase
                                        ))

out.close()