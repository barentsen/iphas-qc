= IPHAS repeat observation priorities =

The script 'assign-repeat-priorities.py' selects IPHAS fields which need to be re-observed, based on the quality control information that has been collected in the table 'iphas-observations.fits'.


== Priority levels ==

The script assigns three priority levels:


=== Priority 1: Missing data ===

The survey would be incomplete without repeating fields in priority 1. 

All previous attempts to observe these fields violate one or more of the following constraints:
* Never passed CASU quality checks
* Seeing > 2.5
* Ellipt > 0.25


=== Priority 2: Poor data ====

Data is available but of poor quality.

Constraints:
* Seeing > 2.0
* Ellipt > 0.2
* Airmass > 2.0
* Sky > 2000 counts


=== Priority 3: Suspect data ===

Data is available within the traditional constraints, but the catalogues indicate one or more problems.

Constraints:
* #stars < 2000
* #stars(r<19.5) / #stars < 10%
* abs(APASS-IPHAS) > 0.5 mag (r' or i')
* abs(SDSS-IPHAS) > 0.5 mag (r' or i')


=== Note ===

Any fields which appear in the file 'fields-done-in-fall-2012.txt' are ignored for re-observation. It is thought they have been observed successfully in September/October 2012.
