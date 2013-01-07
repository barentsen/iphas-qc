#!/bin/bash
# Figure out which fields have been done in the fall 2012 IPHAS runs
python parse-seeing.py
stilts tcopy ifmt=csv ofmt=fits-plus seeing.csv seeing.fits
python fields-done.py | sort | uniq > fields-done-in-fall-2012.txt
