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
    compares photometry between overlapping exposures.
  * **images/**    
    walk through the IPHAS raw data directory and create a table which links
    the images and confidence maps to field numbers.
  * **moon/**
    computes lunar phase and fraction of illumination for each exposure.
  * **observing-logs/**
    download, parse and collate information from the INT telescope observing logs.
  * **quality/**
    assign quality flags to each field.
  * **sdss/**
    compare IPHAS photometry against SDSS data.

The following directories have a cyclic dependency on iphas-observations.fits:
fieldpair-crossmatching, moon, quality