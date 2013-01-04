Quality classification scripts
==============================

These scripts assess the quality of all observations, and identify the best data that is available for each field.

Contents:

quality.py
----------
Assigns quality codes A/B/C/D to each observation using the data available in iphas-qc.fits. Writes output to **quality.csv**.

best-runs.py
------------
Decides on the best 'run' for each field (i.e. the month identifier) based on the data in iphas-qc.fits. Writes output to **best-runs.csv**.