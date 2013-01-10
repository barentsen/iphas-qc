"""
Converts all IPHAS science images to four JPEGs (one per CCD) using 
Montage/mJPEG

Typical command sequence:
funpack r564465.fit.fz
mosaic r564465.fit Ha_conf.fits hamos.fit hamosconf.fit --skyflag=0 --verbose
mJPEG -gray hamos.fit 20% 99.9% log -out hamos.jpg
mJPEG -gray rmos.fit 20% 99.9% log -out rmos.jpg
mJPEG -gray imos.fit 20% 99.9% log -out imos.jpg
convert hamos.jpg rmos.jpg imos.jpg -set colorspace RGB -combine -set colorspace sRGB rgbmos.jpg
"""

import os
import pyfits
import logging
import subprocess
import shlex

""" CONFIGURATION CONSTANTS """
IPHASQC = '/home/gb/dev/iphas-qc/qcdata/iphas-qc.fits'
MOSAIC = '/home/gb/bin/casutools/bin/mosaic'
FPACK = '/home/gb/bin/cfitsio3310/bin/fpack'
FUNPACK = '/home/gb/bin/cfitsio3310/bin/funpack'
MJPEG = '/local/home/gb/bin/Montage_v3.3/mJPEG'
MSHRINK = '/local/home/gb/bin/Montage_v3.3/mShrink'
CONVERT = '/usr/bin/convert'

if os.uname()[1] == 'uhppc11.herts.ac.uk': 
    # Local
    IMAGEPATH = '/media/0133d764-0bfe-4007-a9cc-a7b1f61c4d1d/iphas'
    OUTPATH = '/home/gb/tmp/iphas-quicklook'
    WORKDIR = '/home/gb/tmp/iphas-quicklook-scratch'
else: 
    # Cluster
    MJPEG = '/soft/Montage_v3.3/bin/mJPEG'
    MSHRINK = '/soft/Montage_v3.3/bin/mShrink'

    IMAGEPATH = '/car-data/gb/iphas'
    OUTPATH = '/car-data/gb/iphas-quicklook'
    #WORKDIR = '/stri-data/gb/scratch'
    WORKDIR = '/tmp/gb-scratch'


class Quicklook():
    """ 
    Computes quicklook jpegs for a given IPHAS field.

    Parameters
        :fieldid: (required)
        field identifier string, e.g. '0009o_aug2010'

    Usage
        ql = Quicklook('0009o_aug2010')
        ql.run()
    """

    def __init__(self, fieldid):
        """
        Constructor

        """
        self.fieldid = fieldid
        self.workdir = WORKDIR
        self.filename_root = self.workdir + '/' + self.fieldid

        self.log = logging
        self.qc = pyfits.getdata(IPHASQC, 1)

    def get_fits_filenames(self):
        """
        Returns the location of the three images which make up a field,
        and raises an exception if they cannot be found on the filesystem.

        """
        # Fetch the image filenames from the QC table
        c = self.qc.field('id') == self.fieldid
        img_ha = self.qc.field('image_ha')[c]
        img_r = self.qc.field('image_r')[c]
        img_i = self.qc.field('image_i')[c]
        conf_ha = self.qc.field('conf_ha')[c]
        conf_r = self.qc.field('conf_r')[c]
        conf_i = self.qc.field('conf_i')[c]            
        # Check if we found the filenames, throw an Exception otherwise
        if ( len(img_ha) == 1 & len(img_r) == 1 & len(img_i) == 1
             & len(conf_ha) == 1 & len(conf_r) == 1 & len(conf_i) == 1 
             & (img_ha[0] != '') & (img_r[0] != '') & (img_i[0] != '') 
             & (conf_ha[0] != '') & (conf_r[0] != '') & (conf_i[0] != '') ):
            result = {'img_ha': IMAGEPATH+'/'+img_ha[0],
                    'img_r': IMAGEPATH+'/'+img_r[0], 
                    'img_i': IMAGEPATH+'/'+img_i[0],
                    'conf_ha': IMAGEPATH+'/'+conf_ha[0],
                    'conf_r': IMAGEPATH+'/'+conf_r[0],
                    'conf_i': IMAGEPATH+'/'+conf_i[0] }
            # Test if all the files exist
            for key in result.keys():
                if not os.path.exists( result[key] ):
                    raise Exception('Field %s: file %s does not exist' % (
                            self.fieldid,
                            result[key]) )
            return result
        else:
            raise Exception('Could not find fits filenames for %s' % (
                                self.fieldid) )

    def execute(self, cmd):
        """
        Executes a shell command and logs any errors.

        """
        self.log.debug(cmd)
        p = subprocess.Popen(shlex.split(cmd), 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = p.stdout.read().strip()
        stderr = p.stderr.read().strip()
        if stderr:
            raise Exception("Error detected in quicklook.execute: STDERR={%s} STDOUT={%s} CMD={%s}" % (
                                stderr, stdout, cmd))
        if stdout:
            self.log.debug( stdout )
        return True

    def setup_workdir(self):
        """
        Setup the working directory.

        """
        if not os.path.exists(self.workdir):
            self.execute('mkdir %s' % self.workdir)

    def move_jpegs(self):
        """
        Move the resulting jpegs to their desired location.

        """
        files_to_move = [ self.filename_root + '.jpg',
                          self.filename_root + '_small.jpg' ]
        for band in ['ha', 'r', 'i']:
            files_to_move.append( self.filename_root + '_' + band + '.jpg' )
            files_to_move.append( self.filename_root + '_small_' + band + '.jpg' )
            files_to_move.append(self.filename_root + '_' + band + '.fit')

        for filename in files_to_move:
            cmd = '/bin/mv %s %s' % (
                    filename,
                    OUTPATH )
            self.execute(cmd)

    def clean_workdir(self):
        """
        Remove the working directory.

        """
        files_to_remove = []
        for band in ['ha', 'r', 'i']:
            files_to_remove.append(self.filename_root + '_' + band + '_conf.fit')

        # Delete the leftover fits files
        for filename in files_to_remove:
            cmd = '/bin/rm %s' % (
                   filename )
            self.execute(cmd)

    def compute_jpegs(self):
        assert( os.path.exists(self.workdir) )
        fits_filenames = self.get_fits_filenames()
        
        for band in ['ha', 'r', 'i']:
            filename_fits = self.filename_root + '_' + band + '.fit'
            filename_conf = self.filename_root + '_' + band + '_conf.fit'
            filename_jpg = self.filename_root + '_' + band + '.jpg'
            filename_jpg_small = self.filename_root + '_small_' + band + '.jpg'

            # CASUTools/Mosaic
            cmd = '%s %s %s %s %s --skyflag=0' % (
                MOSAIC,
                fits_filenames['img_' + band],
                fits_filenames['conf_' + band],
                filename_fits,
                filename_conf )
            self.execute(cmd)

            #if not os.path.exists(filename_fits):

            # Montage requires the equinox keyword to be '2000.0'
            # but CASUtools sets the value 'J2000.0'
            myfits = pyfits.open(filename_fits)
            myfits[0].header.update('EQUINOX', '2000.0')
            myfits.writeto(filename_fits, clobber=True)

            # Montage/mJPEG
            cmd = '%s -gray %s 25%% 99.9%% log -out %s' % (
                    MJPEG,
                    filename_fits,
                    filename_jpg )
            self.execute(cmd)


            # Make a smaller version, too
            cmd = '%s %s -resize 600 -quality 70 %s' % (
                    CONVERT,
                    filename_jpg,
                    filename_jpg_small )
            self.execute(cmd)

            """
            # Compress the mosaicked FITS file
            cmd = '%s -D -Y %s' % (
                    FPACK,
                    filename_fits )
            self.execute(cmd)
            """

            # Shrink the mosaicked FITS file
            cmd = '%s %s %s 6' % (
                    MSHRINK,
                    filename_fits,
                    filename_fits )
            self.execute(cmd)
            

        # Final color mosaic
        # Note that we have to ensure that the channels have the same number of pixels
        cmd = '%s %s %s %s -set colorspace RGB -combine -set colorspace sRGB %s' % (
                CONVERT,
                self.filename_root + '_ha.jpg[6210x6145+0+0]',
                self.filename_root + '_r.jpg[6210x6145+0+0]', 
                self.filename_root + '_i.jpg[6210x6145+0+0]', 
                self.filename_root + '.jpg'
                )
        self.execute(cmd)

        # Small version
        cmd = '%s %s -resize 600 -quality 70 %s' % (
                CONVERT,
                self.filename_root + '.jpg',
                self.filename_root + '_small.jpg')
        self.execute(cmd)

    def run(self):
        """
        Main execution loop

        """
        try:
            self.setup_workdir()
            self.compute_jpegs()
            self.move_jpegs()
            self.clean_workdir()
            return True
        except Exception, e:
            self.log.error('Quicklook.run() aborted with exception: "%s"' % e)
            return False



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, 
    format="%(asctime)s/%(levelname)s: %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S" )

    # Nice examples:
    # 7523_sep2005 - cloud 
    # 0026o_nov2003b - seeing jumped to 5 arcsec in r
    # 0027_oct2006b - funny big blob?

    #converter = FieldConverter('5674o_may2007')
    quicklook = Quicklook('0031_nov2003b')
    quicklook.run()
