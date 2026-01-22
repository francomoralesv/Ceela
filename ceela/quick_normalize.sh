#!/bin/bash
# Script rápido para normalizar nombres de archivos

cd "$(dirname "$0")/public/uploads"

find . -depth -name '*' | while read -r file; do
    dir=$(dirname "$file")
    base=$(basename "$file")
    normalized=$(echo "$base" | python3 -c "import sys, unicodedata; print(unicodedata.normalize('NFC', sys.stdin.read().strip()))")

    if [ "$base" != "$normalized" ]; then
        echo "Renombrando: $file -> $dir/$normalized"
        mv "$file" "$dir/$normalized"
    fi
done

echo "✓ Normalización completada"
