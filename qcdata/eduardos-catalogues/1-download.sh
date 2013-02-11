#!/bin/bash

# Download all .mer files from Eduardo's directory at Cambridge
wget -c --mirror --no-parent --no-verbose --http-user=$IPHASUSER --http-passwd=$IPHASPASSWD http://apm3.ast.cam.ac.uk/~eglez/iphas/newmerges/