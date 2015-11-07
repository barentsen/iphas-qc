IPHAS OBSERVING LIST
====================

Contents
--------
This directory lists the outstanding targets for the IPHAS survey:
 * fields.XXh.todo: fields to be observed, grouped by RA. Fields are sorted by
                    priority within each of these files.
 * fields.done: the list of fields which have been observed successfully in
                the past.

*IMPORTANT NOTE*
----------------
To allow us to keep these lists up to date, it is important that you run image 
quality monitoring each night on the 'intdrpc1' machine as follows:

    cd /home/iphas/Seeing
    ./get_seeing.perl

This will write quality information (seeing, ellipticity, sky level, etc) both
to the screen and to a file called 'seeing_YYYYMMDD.log' in the same directory.
***PLEASE E-MAIL THIS FILE AT THE END OF EACH NIGHT TO GEERT@BARENTSEN.BE***

~~~~~~~~~~~~~~~~~~~~~~~~~~~
Contact: geert@barentsen.be
Last update: 20 August 2014
