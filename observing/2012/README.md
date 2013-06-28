= IPHAS repeat observation priorities =

The script 'assign-repeat-priorities.py' selects IPHAS fields which need to be re-observed, based on the quality control information that has been collected in the table 'iphas-qc.fits'.


== QUALITY CONTROL DATA ==

Quality information for all fields reduced by CASU was collated in a table called "iphas-qc.fits".

Apart from the traditional quality control information (seeing/ellipt/sky/airmass), the table includes new quality indicators which have been generated from the catalogues.
The most useful indicators are:
- "n_stars": Number of stellar objects (class=-1 in all bands).
- "f_stars_faint": Percentage of stellar objects (defined as above) fainter than r > 19.5.
- "n_outliers_10p": Number of stellar objects for which r, i or Ha is shifted by >=0.1 mag between on/off-exposures in same run (due to gain variation or fringing).
- "n_outliers_20p": same as above for shifts >=0.2 mag.
- "apass_r" / "apass_i": median shift between IPHAS and APASS (transformed) magnitudes.
- "sdss_r" / "sdss_i": same as above for SDSS DR9.

At this point, let me note that Janet recently sent me the results from the effort of "eyeballing" colour/magnitude diagrams. This revealed that most diagrams which were classified as "sparse" or "lobster" by eye can be selected automatically as follows:
- sparse fields: "f_stars_faint < 20%"
- lobsters: "n_outliers_10p > 50 or n_outliers_20p > 20"


== RE-OBSERVATION PRIORITIES ==

Using the data described above, I generated three lists of fields for re-observation using the following constraints:

= PRIORITY 1: MISSING DATA [105 fields] =
* Never passed CASU quality checks  [79 fields]
* seeing > 2.5  [+9 fields]
* ellipt > 0.25  [+17 fields]

= PRIORITY 2: BAD DATA [+333 fields] =
* seeing > 2.0  [+98 fields]
* ellipt > 0.20  [+84 fields]
* airmass > 2.0  [+1 fields]
* sky > 1500 counts  [+123 fields]
* combination of the above  [+27 fields]

= PRIORITY 3: SUSPECT DATA [+1062 fields] =
* f_stars_faint < 10%  [+249 fields]
* n_stars < 500  [+1 fields]
* n_outliers_20p > 20  [+641 fields]
* n_outliers_10p > 200  [+36 fields]
* sdss_r > 0.5 or sdss_i > 0.5  [+29 fields]
* apass_r > 0.5 or apass_i > 0.5  [+106 fields]



=== Note ===

Any fields which appear in the file 'fields-done-in-fall-2012.txt' are ignored for re-observation. It is thought they have been observed successfully in September/October 2012.
