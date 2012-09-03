#!/bin/bash

stilts tcat in=mikes-dqc-data.csv ifmt=csv \
ocmd="addcol -before run runno parseInt(substring(run,1))" \
ofmt=fits out=mikes-dqc-data.fits

gzip mikes-dqc-data.fits