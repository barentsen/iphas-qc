#!/bin/bash
# Crossmatch iphas-x-sdss stars with information on the anchor fields

STILTS="java -Xmx4000m -jar $HOME/bin/topcat-full.jar -stilts "

$STILTS tmatch2 in1=../../brent-calibration/FINALSOL3.txt ifmt1=ascii \
in2=../iphas_x_sdss.csv ifmt2=csv \
matcher=exact join=1and2 find=all \
values1=id1 values2=id2 \
icmd1='addcol id1 "concat(fld, \"iphas_\", run)"' \
icmd2='addcol id2 "concat(field, dir)"' \
ocmd='keepcols "run fld anchor iphas_ra iphas_dec iphas_r iphas_i sdss_ra sdss_dec sdss_g sdss_r sdss_i";' \
ofmt=fits out=iphas-x-sdss-for-anchors.fits