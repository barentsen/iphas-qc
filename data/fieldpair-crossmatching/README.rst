Fieldpair crossmatching
=======================

The script *crossmatch-mpi.py* compares the photometric catalogues of overlapping exposures. Typically the on- and offset pointings of the same field in the same night are compared. 

The script uses MPI, so run using e.g.
  mpirun -np 8 python do-mosaic-mpi.py

The output is a table called *pairs.csv* which details the number of objects showing a magnitude shift larger than 5/10/20%.

Because only few objects are expected to show brightness shifts exceeding 10/20% within a given night, the measures in the output table is used to detect various data quality problems (e.g. electronic noise, gain variations, extreme fringing.)
