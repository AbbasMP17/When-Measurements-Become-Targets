#!/bin/bash

start="2023-01-01"
end="2026-07-07"

current="$start"

while [ "$(date -d "$current" +%Y%m%d)" -le "$(date -d "$end" +%Y%m%d)" ]
do
    d=$(date -d "$current" +%Y%m%d)

    echo "Processing $d"
    python3 rovista.py "$d"

    current=$(date -d "$current +1 day" +%Y-%m-%d)
done