IPHAS OBSERVING LIST
====================

Contents
--------
This directory lists the outstanding targets for the IPHAS survey:
    * fields.XXh.todo:
        Fields to be observed, grouped by RA. Fields are sorted by observing priority within each of these files.
    * fields.done
        The list of fields which have been observed successfully in the past.

Installation
------------
 1. Download these files to a computer with internet access (e.g. intdrpc1).
 2. Transfer the files to the observing computer under /home/intobs/ha_survey/
 3. Copy the correct fields.todo.XXh file to fields.todo and start observing ("/survey_noguide_err.csh"), following the observing manual at:

    http://apm25.ast.cam.ac.uk/surveys-projects/iphas/internal/Observing/obsman-v3.3.html


*IMPORTANT NOTE*
----------------
To allow us to keep these lists up to date, it is important that you run the image quality monitoring script every night and send us the output as follows:
 1. cd /home/iphas/Seeing (intdrpc1)
 2. ./get_seeing.perl (this will write output both to the screen and to a file 'seeing_YYYYMMDD.log')
 3. At the end of the night, e-mail the file 'seeing_YYYYMMDD.log' for that night to geert@barentsen.be. 
 (The file is written to the same directory as the get_seeing.perl script.)

The 'seeing_YYYYMMDD.log' file provides crucial information to keep the todo lists up to date.

***PLEASE DO NOT FORGET TO E-MAIL THE SEEING LOG FILE AT THE END OF EACH NIGHT TO GEERT@BARENTSEN.BE***

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Contact: geert@barentsen.be
Last update: 10 August 2013
