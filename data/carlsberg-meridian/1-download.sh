#!/bin/bash

# Download night quality data from the Carlsberg Meridian Telescope
mkdir data
for YEAR in 03 04 05 06 07 08 09 10 11 12; do
	wget -P data http://www.ast.cam.ac.uk/ioa/research/cmt/data/camcext.$YEAR
done

# Concatenate all years into a single file. Like a boss.
grep '^[0-9]' data/camcext.* > data/camcext.concatenated
