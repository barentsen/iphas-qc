#!/bin/bash
#
# This script gathers the various sources of quality control data
# and merges them into a single master file using topcat/stilts
#

TMP="/tmp/iphas-fields-observed-tmp.fits"

# Add Brent's anchor info
stilts tmatch2 in1=mikes-mer-files/mer-info.fits.gz ifmt1=fits \
in2=FINALSOL3.txt ifmt2=ascii \
matcher=exact join=all1 find=best \
values1=id values2=id_brent \
icmd1='addcol id "concat(field, \"_\", dir)"' \
icmd2='addcol id_brent "concat(fld, \"_\", run)"; 
	   keepcols "id_brent anchor outZPR-preZPR outZPI-preZPI outZPH-preZPH";' \
ocmd="delcols id_brent" \
ofmt=fits out=$TMP


for FILTER in r i ha; do
	echo "Adding Mike's DQC data for filter $FILTER"

	stilts tmatch2 in1=$TMP ifmt1=fits \
	in2=mikes-dqc-files/mikes-dqc-data.fits.gz ifmt2=fits \
	matcher=exact join=all1 find=best \
	values1="run_$FILTER" values2=runno \
	icmd2='keepcols "runno airmass seeing sky noise ellipt apcor";' \
	ocmd="delcols runno;
	colmeta -name airmass_$FILTER airmass; colmeta -name seeing_$FILTER seeing;
	colmeta -name sky_$FILTER sky; colmeta -name noise_$FILTER noise;
	colmeta -name ellipt_$FILTER ellipt; colmeta -name apcor_$FILTER apcor;
	" \
	ofmt=fits out=$TMP
done


# Add the observing log info
stilts tmatch2 in1=$TMP ifmt1=fits \
in2=observing-logs/logs_byrun.fits.gz ifmt2=fits \
matcher=exact join=all1 find=best \
values1="run_ha" values2="run" \
icmd2='keepcols "run observer temp_avg hum_avg lost_weather lost_technical comments_weather comments_night comments_exposure";' \
ocmd="delcols run;" \
ofmt=fits out=$TMP

# Final arrangement
stilts tcat in=$TMP ifmt=fits \
icmd='addcol airmass "maximum( array(airmass_r, airmass_i, airmass_ha) )";
addcol seeing "maximum( array(seeing_r, seeing_i, seeing_ha) )";
addcol ellipt "maximum( array(ellipt_r, ellipt_i, ellipt_ha) )";' \
ocmd='keepcols "id anchor field dir n_stars seeing ellipt airmass 
fluxr_5sig fluxi_5sig fluxha_5sig 
outZPR-preZPR outZPI-preZPI outZPH-preZPH time 
observer lost_weather lost_technical
hum_avg 
comments_weather comments_night comments_exposure 
run_ha run_r run_i";
colmeta -desc "Anchor column from FINALSOL3.TXT" anchor;
colmeta -desc "Number of objects having class=-1 in all three bands." n_stars;
colmeta -desc "Worst seeing in either of the three bands." -units "arcsec" seeing;
colmeta -desc "Worst ellipticity in either of the three bands." ellipt;
colmeta -desc "Worst airmass in either of the three bands." airmass;
colmeta -name time_r -desc "Time of the r-band exposure." time;
colmeta -desc "Average humidity during the night." -units "percent" hum_avg;
sort id;' \
ofmt=fits out=iphas-fields-observed.fits
