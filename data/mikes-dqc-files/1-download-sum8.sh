#!/bin/bash

# Recursively downloads all *.sum8 files at Cambridge under ~/mike/iphas
wget --mirror --no-parent --no-verbose -A.sum8 --directory-prefix downloaded/ --http-user=$IPHASUSER --http-passwd=$IPHASPASSWD http://apm3.ast.cam.ac.uk/~mike/iphas/
