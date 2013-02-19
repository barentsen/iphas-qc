#!/bin/bash

TARGET=/car-data/gb/iphas-quicklook-thumbnails

for file in `find /car-data/gb/iphas-quicklook -name '*small*jpg'`; do
    filename=`basename $file`
    if [ ! -f $TARGET/$filename ]; then
        echo $TARGET/$filename
        /usr/bin/convert $file -geometry 80 -quality 50 $TARGET/$filename
    fi
done
