#!/bin/bash

# Download all .mer files from Mike's directory at Cambridge
wget --mirror --no-parent --no-verbose -A.mer --http-user=$IPHASUSER --http-passwd=$IPHASPASSWD http://apm3.ast.cam.ac.uk/~mike/iphas/