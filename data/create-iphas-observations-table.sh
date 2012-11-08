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
matcher=exact join=all1 find=best \
values1="night" values2="night" \
fixcols="all" suffix1="" suffix2="_carlsberg" \
ofmt=fits out=$TMP


# Add the SDSS shifts
echo "============================"
echo "Adding in SDSS shifts"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=sdss/shifts.csv.gz ifmt2=csv \
matcher=exact join=all1 find=best \
values1="id" values2="id_sdss" \
suffix1="" \
icmd2='addcol id_sdss "concat(field, \"_\", substring(dir,6))"' \
ofmt=fits out=$TMP

# Add Christine's shifts
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

# Add fieldpair crossmatching results
echo "============================"
echo "Adding in fieldpair crossmatching data"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=fieldpair-crossmatching/fieldpair-info.csv ifmt2=csv \
matcher=exact join=all1 find=best \
values1="mercat" values2="file1" \
fixcols="all" suffix1="" suffix2="_on" \
icmd2='keepcols "file1 n_matched n_outliers_10p n_outliers_20p"' \
ofmt=fits out=$TMP

$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=fieldpair-crossmatching/fieldpair-info.csv ifmt2=csv \
matcher=exact join=all1 find=best \
values1="mercat" values2="file2" \
fixcols="all" suffix1="" suffix2="_off" \
icmd2='keepcols "file2 n_matched n_outliers_10p n_outliers_20p"' \
ofmt=fits out=$TMP


echo "============================"
echo "Adding in starcount ratios (for detecting double images)"
echo "============================"
$STILTS tmatch2 in1=$TMP ifmt1=fits \
in2=double-image-problem/starcount-ratios.csv ifmt2=csv \
matcher=exact join=all1 find=best \
values1="id" values2="id" \
fixcols="dups" suffix1="" suffix2="_ratio" \
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
icmd='addcol sky_max "round( maximum( array(sky_r, sky_i, sky_ha) ) )";
addcol airmass_max "maximum( array(air_r, air_i, air_ha) )";
addcol seeing_max "maximum( array(seeing_r, seeing_i, seeing_ha) )";
addcol ellipt_max "maximum( array(ellipt_r, ellipt_i, ellipt_ha) )";
addcol sky_min "round( minimum( array(sky_r, sky_i, sky_ha) ) )";
addcol airmass_min "minimum( array(air_r, air_i, air_ha) )";
addcol seeing_min "minimum( array(seeing_r, seeing_i, seeing_ha) )";
addcol ellipt_min "minimum( array(ellipt_r, ellipt_i, ellipt_ha) )";
addcol f_stars_faint "roundDecimal(100.0 * n_stars_faint / toFloat(n_stars), 1)";
addcol n_matched "NULL_n_matched_on ? n_matched_off : n_matched_on";
addcol n_outliers_10p "NULL_n_outliers_10p_on ? n_outliers_10p_off : n_outliers_10p_on";
addcol n_outliers_20p "NULL_n_outliers_20p_on ? n_outliers_20p_off : n_outliers_20p_on";
addcol f_outliers_10p "100.0 * n_outliers_10p / toFloat(n_matched)"
addcol f_outliers_20p "100.0 * n_outliers_20p / toFloat(n_matched)"
addcol ra "hmsToDegrees(ra_r)";
addcol dec "dmsToDegrees(dec_r)";
addcol is_anchor "anchor == 1";
addcol is_penultimate_release "anchor == 0 || anchor == 1";
addcol is_quality_ok "seeing_max < 2.0 & ellipt_max < 0.20 & airmass_max < 2.0 & sky_max < 1500 & f_stars_faint > 10";' \
ocmd='addskycoords -inunit deg -outunit deg fk5 galactic ra dec l b;
keepcols "id anchor field dir n_stars 
n_bright_ha n_bright_r n_bright_i
ratio_bright_ha ratio_bright_r ratio_bright_i
f_stars_faint r90p 
n_outliers_10p n_outliers_20p f_outliers_10p f_outliers_20p	
seeing_max ellipt_max airmass_max sky_max
seeing_min ellipt_min airmass_min sky_min
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
ra dec l b
run_ha run_r run_i
mercat
is_anchor is_penultimate_release
is_quality_ok";
colmeta -desc "Right Ascension of the r-band exposure." ra;
colmeta -desc "Declination of the r-band exposure." dec;
colmeta -desc "r-band zeropoint from Eduardo''s mercat header." zpr;
colmeta -desc "i-band zeropoint from Eduardo''s mercat header." zpi;
colmeta -desc "ha-band zeropoint from Eduardo''s mercat header." zph;
colmeta -desc "r-band zeropoint from FINALSOL3 (or anchor-zp-shifts.asc if given!)" zpr_calib;
colmeta -desc "i-band zeropoint from FINALSOL3 (or anchor-zp-shifts.asc if given!)" zpi_calib;
colmeta -desc "ha-band zeropoint from FINALSOL3 (or anchor-zp-shifts.asc if given!)" zph_calib;
colmeta -desc "median(IPHAS_r - SDSS_DR9_r_transformed)" sdss_r;
colmeta -desc "median(IPHAS_i - SDSS_DR9_i_transformed)" sdss_i;
colmeta -desc "median(IPHAS_r - APASS_r_transformed)" apass_r;
colmeta -desc "median(IPHAS_i - APASS_i_transformed)" apass_i;
colmeta -desc "Anchor column from FINALSOL3.TXT" anchor;
colmeta -desc "Number of stellar objects (class=-1 in all bands)." n_stars;
colmeta -desc "Ratio: n_stars_ha(on-field) / n_stars_ha(off-field); helps to detect images with duplicate stars." ratio_bright_ha;
colmeta -desc "Ratio: n_stars_r(on-field) / n_stars_ha(off-field); helps to detect images with duplicate stars." ratio_bright_r;
colmeta -desc "Ratio: n_stars_i(on-field) / n_stars_ha(off-field); helps to detect images with duplicate stars." ratio_bright_i;
colmeta -desc "Percentage of stellar objects fainter than r > 19.5." -units "percent" f_stars_faint;
colmeta -desc "90-percentile of the r magnitudes of stars." r90p;
colmeta -desc "Number of stellar objects for which the r, i or Ha shifted by >=0.1 mag between same-run on/off-exposures (due to gain variation or fringing)." n_outliers_10p;
colmeta -desc "Number of stellar objects for which the r, i or Ha shifted by >=0.2 mag between same-run on/off-exposures (due to gain variation or fringing)." n_outliers_20p;
colmeta -desc "Maximum (worst) seeing of the three single-filter exposures." -units "arcsec" seeing_max;
colmeta -desc "Maximum (worst) ellipticity of the three single-filter exposures." ellipt_max;
colmeta -desc "Maximum (worst) airmass of the three single-filter exposures." airmass_max;
colmeta -desc "Minimum (best) seeing of the three single-filter exposures." -units "arcsec" seeing_min;
colmeta -desc "Minimum (best) ellipticity of the three single-filter exposures." ellipt_min;
colmeta -desc "Minimum (best) airmass of the three single-filter exposures." airmass_min;
colmeta -name time_r -desc "Time of the r-band exposure." time;
colmeta -desc "Median extinction in r during the night, measured by the Carlsberg Meridian Telescope. : indicates an uncertain value due to the night probably not being photometric. " ext_r_carlsberg;
colmeta -desc "Number of hours of photometric data taken by the Carlsberg Meridian Telescope that night." hours_phot_carlsberg;
colmeta -desc "Number of non-photometric hours that night." hours_nonphot_carlsberg;
colmeta -desc "Average humidity during the night." -units "percent" hum_avg;
colmeta -desc "Are the various quality indicators (seeing, ellipticity, etc) within spec?" is_quality_ok;
sort id;' \
ofmt=fits out=iphas-observations.fits
