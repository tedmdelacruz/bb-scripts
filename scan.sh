#!/bin/bash

TARGET=$1
RECON_DIR="$HOME/recon"

TARGET_DIR="$RECON_DIR/$TARGET"

if [ ! -d "$TARGET_DIR/.tmp" ]; then
    mkdir "$TARGET_DIR/.tmp"
fi;

cp "$TARGET_DIR/subdomains.txt" "$TARGET_DIR/.tmp/subdomains.txt"

subfinder -v -dL $TARGET_DIR/wildcards.txt -o $TARGET_DIR/subdomains.txt

cat $TARGET_DIR/subdomains.txt | sort -u -o $TARGET_DIR/subdomains.txt

cat $TARGET_DIR/subdomains.txt | anew $TARGET_DIR/.tmp/subdomains.txt > $TARGET_DIR/.tmp/new.txt

if [ ! -d "$TARGET_DIR/.history" ]; then
    mkdir "$TARGET_DIR/.history"
fi;

if [ -s "$TARGET_DIR/.tmp/new.txt" ];then
    now=$(date +%s)
    cp "$TARGET_DIR/.tmp/new.txt" "$TARGET_DIR/.history/$now"
    NUM_SUBDOMAINS=$(wc -l "$TARGET_DIR/.tmp/new.txt" | awk '{print $1}')
    echo "Found $NUM_SUBDOMAINS new subdomains for target: **$TARGET**" | notify -id general
fi;
