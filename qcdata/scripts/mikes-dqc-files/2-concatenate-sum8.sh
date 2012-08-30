#!/bin/bash

# This script will run through Mike's iphas directory and concatenate all 
# the summary.sum8 files into a single "sum8.concatenated" file

OUTPUT="sum8.concatenated"

# Copy the header line from one of the files
HEADER=`head -n1 "downloaded/apm3.ast.cam.ac.uk/~mike/iphas/aug2010/dqcinfo/summary.sum8"`
echo $HEADER > $OUTPUT

# Now copy the contents of all summary.sum8 files, except the header line
for FILE in `find downloaded/ -name "summary.sum8"`; do
	echo "Adding $FILE"
	# Name of the run (e.g. oct2009) is the name of the 5th-level subdirectory
	RUNMONTH=`echo $FILE | cut -d"/" -f5`
	# Pad the string with spaces to respect the "fixed width" ascii format
	RUNMONTH_PADDED=`printf %15s $RUNMONTH`
	# --invert-match is used to grep everything EXCEPT the header line
	# sed is used to prefix every line with the padded runmonth
	grep --invert-match "Run" $FILE | grep --invert-match '^$' | sed -e "s/^/$RUNMONTH_PADDED /" > /tmp/sum8
	cat /tmp/sum8 >> $OUTPUT
done
