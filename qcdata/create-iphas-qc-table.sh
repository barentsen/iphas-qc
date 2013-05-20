#!/bin/bash
#
# This script gathers the various sources of quality control data
# and merges them into a single master file using topcat/stilts
#

java -version

TMP="/tmp/iphas-qc-tmp.fits"
STILTS="java -Xmx2000m -XX:+UseConcMarkSweepGC -jar $HOME/bin/topcat-full.jar -stilts "

# Adding in Brent's anchor info
echo "============================"
echo "Start from catalogue summaries and add in Brent's FINALSOL3"
echo "============================"
$STILTS tmatch2 in1=eduardos-catalogues/mercat-info.csv ifmt1=csv \
in2=brent-calibration/FINALSOL3.txt ifmt2=ascii \
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
addcol zpr_finalsol3 "(NULL_zpr_preferred || anchor == 0) ? zpr_brent : zpr_preferred";
addcol zpi_finalsol3 "(NULL_zpi_preferred || anchor == 0) ? zpi_brent : zpi_preferred";
addcol zph_finalsol3 "(NULL_zph_preferred || anchor == 0) ? zph_brent : zph_preferred";
' \
ofmt=fits out=$TMP


for FILTER in r i ha; do
	echo "============================"
	echo "Adding Mike Irwin's DQC data for filter $FILTER"
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

echo "============================"
echo "Adding observing logs"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=observing-logs/logs_byrun.fits.gz ifmt2=fits \
matcher=exact join=all1 find=best \
values1="run_ha" values2="run" \
icmd2='keepcols "run night observer temp_avg hum_avg lost_weather lost_technical comments_weather comments_night comments_exposure";' \
ocmd="delcols run;" \
ofmt=fits out=$TMP

echo "============================"
echo "Adding filenames of images     "
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=images/iphas-images.csv ifmt2=csv \
icmd2='keepcols "run image conf_ha";' \
matcher=exact join=all1 find=best \
values1="run_ha" values2="run" \
ocmd='addcol image_ha "image"; delcols "run image";' \
ofmt=fits out=$TMP

$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=images/iphas-images.csv ifmt2=csv \
icmd2='keepcols "run image conf_r";' \
matcher=exact join=all1 find=best \
values1="run_r" values2="run" \
ocmd='addcol image_r "image"; delcols "run image";' \
ofmt=fits out=$TMP

$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=images/iphas-images.csv ifmt2=csv \
icmd2='keepcols "run image conf_i";' \
matcher=exact join=all1 find=best \
values1="run_i" values2="run" \
ocmd='addcol image_i "image"; delcols "run image";' \
ofmt=fits out=$TMP

echo "============================"
echo "Adding in Carlsberg Meridian Telescope sky quality data"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=carlsberg-meridian/carlsberg.csv ifmt2=csv \
matcher=exact join=all1 find=best1 \
values1="night" values2="night" \
fixcols="all" suffix1="" suffix2="_carlsberg" \
ofmt=fits out=$TMP

echo "============================"
echo "Adding in SDSS shifts"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=sdss/shifts.csv.gz ifmt2=csv \
matcher=exact join=all1 find=best1 \
values1="id" values2="id_sdss" \
suffix1="" \
icmd2='addcol id_sdss "concat(field, \"_\", substring(dir,6))"' \
ofmt=fits out=$TMP

echo "============================"
echo "Adding in fieldpair crossmatching data"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=fieldpair-crossmatching/pairs.csv ifmt2=csv \
matcher=exact join=all1 find=best1 \
values1="id" values2="id" \
fixcols="dups" suffix1="" suffix2="_pairscsv" \
icmd2='keepcols "id n_matched n_outliers_10p n_outliers_20p f_outliers_10p f_outliers_20p n_20p_r n_20p_i n_20p_h is_samenightpair"' \
ofmt=fits out=$TMP

echo "============================"
echo "Adding in moon data"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=moon/moon.csv ifmt2=csv \
matcher=exact join=all1 find=best1 \
values1="id" values2="id" \
fixcols="dups" suffix1="" suffix2="_moon" \
ofmt=fits out=$TMP

echo "============================"
echo "Adding in quality flags (A++, A+, A, B, C)"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=quality/quality.csv ifmt2=csv \
matcher=exact join=all1 find=best1 \
values1="id" values2="id" \
fixcols="dups" suffix1="" suffix2="_qual" \
ofmt=fits out=$TMP

echo "============================"
echo "Adding in the is_best column"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=quality/best-runs.csv ifmt2=csv \
matcher=exact join=all1 find=best1 \
values1="id" values2="id" \
fixcols="dups" suffix1="" suffix2="_qual" \
ofmt=fits out=$TMP

echo "============================"
echo "Adding in new APASS shifts"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=apass/20130520-shifts.fits ifmt2=fits \
matcher=exact join=all1 find=best1 \
values1="id" values2="Field" \
fixcols="all" suffix1="" suffix2="_apassdr7" \
ofmt=fits out=$TMP

# Final arrangement
echo "============================"
echo "Gotterdammerung"
echo "============================"
$STILTS tcat in=$TMP ifmt=fits \
icmd='addcol sky_max "round( maximum( array(sky_r, sky_i, sky_ha) ) )";
addcol airmass_max "maximum( array(air_r, air_i, air_ha) )";
addcol seeing_max "maximum( array(seeing_r, seeing_i, seeing_ha) )";
addcol ellipt_max "maximum( array(ellipt_r, ellipt_i, ellipt_ha) )";
addcol sky_min "round( minimum( array(sky_r, sky_i, sky_ha) ) )";
addcol airmass_min "minimum( array(air_r, air_i, air_ha) )";
addcol seeing_min "minimum( array(seeing_r, seeing_i, seeing_ha) )";
addcol ellipt_min "minimum( array(ellipt_r, ellipt_i, ellipt_ha) )";
addcol mjd "isoToMjd(time)";
addcol ra "hmsToDegrees(ra_r)";
addcol dec "dmsToDegrees(dec_r)";
addcol is_anchor "anchor == 1";
addcol is_finalsol3 "anchor == 0 || anchor == 1";
addcol is_offset "field.endsWith(\"o\")";' \
ocmd='addskycoords -inunit deg -outunit deg fk5 galactic ra dec l b;
keepcols "id anchor field dir n_stars n_objects
rmode rmedian
r5sig i5sig h5sig
n_outliers_10p n_outliers_20p	
f_outliers_10p f_outliers_20p
n_20p_r n_20p_i n_20p_h
is_samenightpair
seeing_max ellipt_max airmass_max sky_max
seeing_min ellipt_min airmass_min sky_min
n_stars_r n_stars_i n_stars_ha
seeing_r seeing_i seeing_ha
ellipt_r ellipt_i ellipt_ha
zpr zpi zph 
e_zpr e_zpi e_zpha
zpr_finalsol3 zpi_finalsol3 zph_finalsol3
sdss_stars sdss_r sdss_i
apass_stars apass_r apass_i
time mjd night
ext_r_carlsberg hours_phot_carlsberg hours_nonphot_carlsberg
observer lost_weather lost_technical
hum_avg 
comments_weather comments_night comments_exposure 
moon_altitude moon_separation moon_phase
ra dec l b
run_ha run_r run_i
image_ha image_r image_i
conf_ha conf_r conf_i
mercat
is_anchor is_finalsol3 
rmode_judged rmedian_judged r5sig_judged i5sig_judged h5sig_judged 
problems problems_simple qflag
is_ok is_best
rshift_apassdr7 ishift_apassdr7 rmatch_apassdr7 imatch_apassdr7
";
colmeta -desc "Right Ascension of the r-band exposure." ra;
colmeta -desc "Declination of the r-band exposure." dec;
colmeta -desc "r-band zeropoint from Eduardo''s mercat header." zpr;
colmeta -desc "i-band zeropoint from Eduardo''s mercat header." zpi;
colmeta -desc "ha-band zeropoint from Eduardo''s mercat header." zph;
colmeta -desc "r-band zeropoint from FINALSOL3 (or anchor-zp-shifts.asc if given!)" zpr_finalsol3;
colmeta -desc "i-band zeropoint from FINALSOL3 (or anchor-zp-shifts.asc if given!)" zpi_finalsol3;
colmeta -desc "ha-band zeropoint from FINALSOL3 (or anchor-zp-shifts.asc if given!)" zph_finalsol3;
colmeta -desc "median(IPHAS_r - SDSS_DR9_r_transformed)" sdss_r;
colmeta -desc "median(IPHAS_i - SDSS_DR9_i_transformed)" sdss_i;
colmeta -desc "median(IPHAS_r - APASS_r_transformed)" apass_r;
colmeta -desc "median(IPHAS_i - APASS_i_transformed)" apass_i;
colmeta -desc "Anchor column from FINALSOL3.TXT" anchor;
colmeta -desc "Number of stellar objects (class=-1 in all bands)." n_stars;
colmeta -desc "Number of objects in the r band (any class)." n_objects;
colmeta -desc "Mode of the r magnitude distribution for those objects which are detected and classified as stellar or probably stellar in both the r and i bands. Used as a proxy for completeness." rmode;
colmeta -desc "Median r magnitude of stars detected at SNR=5, i.e. where the photometric errors are 0.2 mag." r5sig;
colmeta -desc "Median i magnitude of stars detected at SNR=5, i.e. where the photometric errors are 0.2 mag." i5sig;
colmeta -desc "Median H-alpha magnitude of stars detected at SNR=5, i.e. where the photometric errors are 0.2 mag." h5sig;
colmeta -desc "Fraction of stellar objects for which r/i/Ha shifted by >=0.1 mag between same-run on/off-exposures (typically due to gain variation or fringing)." f_outliers_10p;
colmeta -desc "Fraction of stellar objects for which r/i/Ha shifted by >=0.2 mag between same-run on/off-exposures (typically due to gain variation or fringing)." f_outliers_20p;
colmeta -desc "Maximum (worst) seeing of the three single-filter exposures." -units "arcsec" seeing_max;
colmeta -desc "Maximum (worst) ellipticity of the three single-filter exposures." ellipt_max;
colmeta -desc "Maximum (worst) airmass of the three single-filter exposures." airmass_max;
colmeta -desc "Minimum (best) seeing of the three single-filter exposures." -units "arcsec" seeing_min;
colmeta -desc "Minimum (best) ellipticity of the three single-filter exposures." ellipt_min;
colmeta -desc "Minimum (best) airmass of the three single-filter exposures." airmass_min;
colmeta -name time_r -desc "Time of the r-band exposure." time;
colmeta -desc "Modified Julian Date of the r-band exposure." mjd;
colmeta -desc "Median extinction in r during the night, measured by the Carlsberg Meridian Telescope. : indicates an uncertain value due to the night probably not being photometric. " ext_r_carlsberg;
colmeta -desc "Number of hours of photometric data taken by the Carlsberg Meridian Telescope that night." hours_phot_carlsberg;
colmeta -desc "Number of non-photometric hours that night." hours_nonphot_carlsberg;
colmeta -desc "Average humidity during the night." -units "percent" hum_avg;
colmeta -desc "Phase of the moon at the time the r-band exposure was taken." -units "percent" moon_phase;
colmeta -desc "Altitude of the moon at the time the r-band exposure was taken." -units "degrees" moon_altitude;
colmeta -desc "Separation of the moon and the r-band exposure." -units "degrees" moon_separation;
colmeta -desc "INT run number for ha-band image." run_ha;
colmeta -desc "INT run number for r-band image." run_r;
colmeta -desc "INT run number for i-band image." run_i;
colmeta -desc "Filename of the reduced H-alpha image." image_ha;
colmeta -desc "Filename of the reduced r-band image." image_r;
colmeta -desc "Filename of the reduced i-band image." image_i;
colmeta -desc "Filename of the H-alpha confidence map." conf_ha;
colmeta -desc "Are the various quality indicators (seeing, ellipticity, etc) within spec?" is_ok;
colmeta -desc "Is it the best data available for the given field?" is_best;
sort id;' \
ofmt=fits out=iphas-qc.fits

# Run the regression test
echo "============================"
echo "Regression tests"
echo "============================"
python tests/test.py

# Copy to web directory
cp iphas-qc.fits ~/public_html/iphas-qc
