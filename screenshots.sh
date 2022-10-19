#!/bin/bash

TARGET=$1
RECON_DIR="$HOME/recon"
TARGET_DIR="$RECON_DIR/$TARGET"

cat http.txt | aquatone \
-ports=80,443,8080,8081,8443,8000 \
-resolution=800,600 -debug -threads=5 \
-chrome-path=$CHROME_PATH \ 
-out $TARGET_DIR/screenshots && echo "Done taking screenshots on $TARGET" | notify -id general
