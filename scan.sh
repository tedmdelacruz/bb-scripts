TARGET=$1
RECON_DIR="/root/recon"

TARGET_DIR="$RECON_DIR/$TARGET"

echo "Enumerating subdomains for target: **$TARGET**" | notify -id general

if [ ! -d "$TARGET_DIR/.tmp" ]; then
    echo "Creating $TARGET_DIR/.tmp"
    mkdir "$TARGET_DIR/.tmp"
fi;

cp "$TARGET_DIR/subfinder.txt" "$TARGET_DIR/.tmp/subfinder.txt"

subfinder -v -dL $TARGET_DIR/wildcards.txt -o $TARGET_DIR/subfinder.txt && echo "Done running subfinder"

cat $TARGET_DIR/subfinder.txt | sort -u -o $TARGET_DIR/subfinder.txt

comm -3 "$TARGET_DIR/subfinder.txt" "$TARGET_DIR/.tmp/subfinder.txt" > "$TARGET_DIR/.tmp/subfinder.comm"

if [ -s "$TARGET_DIR/.tmp/subfinder.comm" ];then
    NUM_SUBDOMAINS=$(wc -l "$TARGET_DIR/.tmp/subfinder.comm" | awk '{print $1}')
    echo "Found new $NUM_SUBDOMAINS subdomains for target: **$TARGET**" | notify -id general
else
    echo "No new subdomains found for target: **$TARGET**" | notify -id general
fi;
