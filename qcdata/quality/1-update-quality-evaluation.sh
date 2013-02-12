# Warnings: both quality.py and best-runs.py 
# read/provide data for iphas-qc.fits,
# hence, this table needs to be updated before/after running these scripts.

# Assign quality flags to each field observation
python quality.py
# Incorporate these flags in the master table
cd ..
./create-iphas-qc-table.sh
# Now decide which observations provide the best data per field ('is_best')
cd quality
python best-runs.py
# Incorporate the 'is_best' column in the master table
cd ..
./create-iphas-qc-table.sh
cd quality
echo "ALL IS DONE"