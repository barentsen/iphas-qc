#!/bin/bash
#
# This script gathers the various sources of quality control data
# and merges them into a single master file using topcat/stilts
#

TMP="/tmp/iphas-fields-observed-tmp.fits"
STILTS="java -Xmx4000m -jar $HOME/bin/topcat-full.jar -stilts "

# Adding in Brent's anchor info
echo "============================"
echo "Adding in Brent's FINALSOL3"
echo "============================"
$STILTS tmatch2 in1=eduardos-catalogues/mercat-info.csv ifmt1=csv \
in2=FINALSOL3.txt ifmt2=ascii \
matcher=exact join=all1 find=best \
values1=id values2=id_brent \
suffix1="" \
icmd1='addcol id "concat(field, \"_\", substring(dir,6))"' \
icmd2='addcol id_brent "concat(fld, \"_\", run)"; 
	   keepcols "id_brent anchor  
	   			 outZPR-preZPR outZPI-preZPI outZPH-preZPH";' \
ocmd='colmeta -name zpr_diff -desc "outZPR-preZPR from FINALSOL3.TXT" outZPR-preZPR;
colmeta -name zpi_diff -desc "outZPI-preZPI from FINALSOL3.TXT" outZPI-preZPI;
colmeta -name zph_diff -desc "outZPH-preZPH from FINALSOL3.TXT" outZPH-preZPH;
addcol zpr_brent "zpr + zpr_diff";
addcol zpi_brent "zpi + zpi_diff";
addcol zph_brent "zph + zph_diff";
' \
ofmt=fits out=$TMP



# Adding in manually edited anchor zeropoints
echo "============================"
echo "Adding in anchor zeropoint shifts"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=brent-anchor-shifts/anchor-zp-shifts.fits ifmt2=fits \
matcher=exact join=all1 find=best \
values1=id_brent values2=id \
suffix1="" \
icmd2='keepcols "id zpr_preferred zpi_preferred zph_preferred";' \
ocmd='delcols "id_brent";
addcol zpr_calib "(NULL_zpr_preferred || anchor == 0) ? zpr_brent : zpr_preferred";
addcol zpi_calib "(NULL_zpi_preferred || anchor == 0) ? zpi_brent : zpi_preferred";
addcol zph_calib "(NULL_zph_preferred || anchor == 0) ? zph_brent : zph_preferred";
' \
ofmt=fits out=$TMP



for FILTER in r i ha; do
	echo "============================"
	echo "Adding Mike's DQC data for filter $FILTER"
	echo "============================"
	$STILTS tmatch2 in1=$TMP ifmt1=fits \
	in2=mikes-dqc-files/mikes-dqc-data.fits.gz ifmt2=fits \
	matcher=exact join=all1 find=best \
	values1="run_$FILTER" values2=runno \
	icmd2='keepcols "runno ra dec seeing sky noise ellipt apcor";' \
	ocmd="delcols runno;
	colmeta -name ra_$FILTER ra;
	colmeta -name dec_$FILTER dec;
	colmeta -name seeing_$FILTER seeing;
	colmeta -name sky_$FILTER sky; 
	colmeta -name noise_$FILTER noise;
	colmeta -name ellipt_$FILTER ellipt; 
	colmeta -name apcor_$FILTER apcor;
	" \
	ofmt=fits out=$TMP
done

# Add Carlsberg Meridian Telescope info
#carlsberg.csv

# Add the observing log info
echo "============================"
echo "Adding in the observing logs"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=observing-logs/logs_byrun.fits.gz ifmt2=fits \
matcher=exact join=all1 find=best \
values1="run_ha" values2="run" \
icmd2='keepcols "run night observer temp_avg hum_avg lost_weather lost_technical comments_weather comments_night comments_exposure";' \
ocmd="delcols run;" \
ofmt=fits out=$TMP

# Add the Carlsberg Meridian Telescope sky quality data
echo "============================"
echo "Adding in Carlsberg Meridian"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=carlsberg-meridian/carlsberg.csv ifmt2=csv \
matcher=exact join=all1 find=all \
values1="night" values2="night" \
fixcols="all" suffix1="" suffix2="_carlsberg" \
ofmt=fits out=$TMP


# Add the SDSS shifts
echo "============================"
echo "Adding in SDSS shifts"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=sdss/shifts.csv ifmt2=csv \
matcher=exact join=all1 find=best \
values1="id" values2="id_sdss" \
suffix1="" \
icmd2='addcol id_sdss "concat(field, \"_\", substring(dir,6))"' \
ofmt=fits out=$TMP

# Add the SDSS shifts
echo "============================"
echo "Adding in Christine's shifts"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=christine-apass/apass_calibration.fits ifmt2=fits \
matcher=exact join=all1 find=best \
values1="id" values2="id_christine" \
fixcols="all" suffix1="" suffix2="_christine" \
icmd2='addcol id_christine "concat(field, \"_\", run)"' \
ofmt=fits out=$TMP

# Add eyeballing info
#echo "============================"
#echo "Adding in eyeballing comments"
#echo "============================"
#$STILTS tmatch2 in1=$TMP ifmt1=fits \
#in2=eyeballing/concatenated.asc ifmt2=ascii \
#matcher=exact join=all1 find=best \
#values1="id" values2="id_christine" \
#fixcols="all" suffix1="" suffix2="_christine" \
#icmd2='addcol id_christine "concat(field, \"_\", run)"' \
#ofmt=fits out=$TMP

# Final arrangement
echo "============================"
echo "Gotterdammerung"
echo "============================"
$STILTS tcat in=$TMP ifmt=fits \
icmd='addcol airmass_worst "maximum( array(air_r, air_i, air_ha) )";
addcol seeing_worst "maximum( array(seeing_r, seeing_i, seeing_ha) )";
addcol ellipt_worst "maximum( array(ellipt_r, ellipt_i, ellipt_ha) )";
addcol ra "hmsToDegrees(ra_r)";
addcol dec "dmsToDegrees(dec_r)";
addcol is_anchor "anchor == 1";
addcol is_penultimate_release "anchor == 0 || anchor == 1";' \
ocmd='keepcols "id anchor field dir n_stars n_stars_gt20 r90p
seeing_worst ellipt_worst airmass_worst 
fluxr_5sig fluxi_5sig fluxha_5sig 
zpr zpi zph 
e_zpr e_zpi e_zpha
zpr_calib zpi_calib zph_calib
sdss_stars sdss_r sdss_i
apass_stars apass_r apass_i
shift_r_christine shift_i_christine shift_h_christine apass_shift_r_christine apass_shift_i_christine
time night
ext_r_carlsberg hours_phot_carlsberg hours_nonphot_carlsberg
observer lost_weather lost_technical
hum_avg 
comments_weather comments_night comments_exposure 
ra dec
run_ha run_r run_i
mercat
is_anchor is_penultimate_release";
colmeta -desc "r-band zeropoint from Eduardo''s mercat header." zpr;
colmeta -desc "i-band zeropoint from Eduardo''s mercat header." zpi;
colmeta -desc "ha-band zeropoint from Eduardo''s mercat header." zph;
colmeta -desc "r-band zeropoint from FINALSOL3 (or anchor-zp-shifts.asc if given!)" zpr_calib;
colmeta -desc "i-band zeropoint from FINALSOL3 (or anchor-zp-shifts.asc if given!)" zpi_calib;
colmeta -desc "ha-band zeropoint from FINALSOL3 (or anchor-zp-shifts.asc if given!)" zph_calib;
colmeta -desc "median(IPHAS_r - SDSS_DR9_r_transformed)" sdss_r;
colmeta -desc "median(IPHAS_r - SDSS_DR9_i_transformed)" sdss_i;
colmeta -desc "Anchor column from FINALSOL3.TXT" anchor;
colmeta -desc "Number of stars (class=-1 in all bands)." n_stars;
colmeta -desc "Number of stars fainter than r > 20 (class=-1 in all bands)." n_stars_gt20;
colmeta -desc "90-percentile of the r magnitudes of stars." r90p;
colmeta -desc "Worst seeing in either of the three bands." -units "arcsec" seeing_worst;
colmeta -desc "Worst ellipticity in either of the three bands." ellipt_worst;
colmeta -desc "Worst airmass in either of the three bands." airmass_worst;
colmeta -name time_r -desc "Time of the r-band exposure." time;
colmeta -desc "Median extinction in r during the night, measured by the Carlsberg Meridian Telescope. : indicates an uncertain value due to the night probably not being photometric. " ext_r_carlsberg;
colmeta -desc "Number of hours of photometric data taken by the Carlsberg Meridian Telescope that night." hours_phot_carlsberg;
colmeta -desc "Number of non-photometric hours that night." hours_nonphot_carlsberg;
colmeta -desc "Average humidity during the night." -units "percent" hum_avg;
sort id;' \
ofmt=fits out=iphas-observations.fits
