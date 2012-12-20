Fieldpair crossmatching
=======================

The script *crossmatch-fieldpairs.py* compares the photometric catalogues of fields which were observed at the on- and offset pointing in the same night. It produces a table called *fieldpair-info.csv* which details the number of objects showing a magnitude shift larger than 5/10/20%.

Because only few objects are expected to show brightness shifts exceeding 10/20% within a given night, the measures in the output table is used to detect various problems (e.g. electronic noise, gain variations, extreme fringing events.)
