#!/bin/bash

TARGET=$1
RECON_DIR="/root/recon"

TARGET_DIR="$RECON_DIR/$TARGET"

echo "Enumerating subdomains for target: **$TARGET**" | notify -id general

if [ ! -d "$TARGET_DIR/.tmp" ]; then
    echo "Creating $TARGET_DIR/.tmp"
    mkdir "$TARGET_DIR/.tmp"
fi;

cp "$TARGET_DIR/subdomains.txt" "$TARGET_DIR/.tmp/subdomains.txt"

subfinder -v -dL $TARGET_DIR/wildcards.txt -o $TARGET_DIR/subdomains.txt && echo "Done running subdomains"

cat $TARGET_DIR/subdomains.txt | sort -u -o $TARGET_DIR/subdomains.txt

cat $TARGET_DIR/subdomains.txt | anew $TARGET_DIR/.tmp/subdomains.txt > $TARGET_DIR/.tmp/subdomains.new

if [ -s "$TARGET_DIR/.tmp/subdomains.new" ];then
    NUM_SUBDOMAINS=$(wc -l "$TARGET_DIR/.tmp/subdomains.new" | awk '{print $1}')
    echo "Found $NUM_SUBDOMAINS new subdomains for target: **$TARGET**" | notify -id general
else
    echo "No new subdomains found for target: **$TARGET**" | notify -id general
fi;
