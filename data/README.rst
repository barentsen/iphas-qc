==========================
IPHAS Quality Control Data
==========================

This directory contains all the bits and pieces required to create the table
*iphas-observations.fits*, containing all the essential metadata and quality control 
information on observations carried out as part of the IPHAS survey.

This master table is generated using the shell script *create-iphas-observations-table.sh*, 
which collates data from the different subdirectories using TopCat/stilts.

Contents
========

Various scripts to obtain and analyse parts of the meta data can be found in the sub-directories:
  * **fieldpair-crossmatching/**
    compares photometry between the two pointings that make up each field.
 * **observing-logs/**: download, parse and collate information from the INT telescope observing logs.
 * **quality/**: assign quality flags to each field.
 * **sdss/**: compare IPHAS photometry against SDSS data.
