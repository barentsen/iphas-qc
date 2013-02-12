Quality evaluation scripts
==========================

These scripts assess the quality of all observations and assign quality flags (columns 'problems', 'qflag' and 'is_ok' in *iphas-qc.fits*.) These flags are then used to identify the best epoch that is available for each field (column 'is_best' in *iphas-qc.fits*.)

Usage
-----

    ./1-update-quality-evaluation.sh

Contents
--------

blacklist.txt
~~~~~~~~~~~~~
List of fields which should be D-graded, regardless of their QC information.

whitelist.txt
~~~~~~~~~~~~~
List of fields to be A-graded, regardless of their QC information.

quality.py
~~~~~~~~~~
Assigns quality codes A/B/C/D to each observation using the data available in iphas-qc.fits. This script takes *blacklist.txt* and *whitelist.txt* into account, and writes its output to *quality.csv*.

best-runs.py
~~~~~~~~~~~~
Decides on the best 'run' for each field (i.e. the month identifier) based on the data in iphas-qc.fits. Writes output to *best-runs.csv*.
