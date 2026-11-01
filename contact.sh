#!/usr/bin/env bash
# contact.sh <mp4> <out.png>: 6 frames spread over the clip, 3x2 sheet
f="$1"; o="$2"; d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
t=$(mktemp -d); for i in 0 1 2 3 4 5; do ts=$(python3 -c "print(round($d*($i+0.5)/6 if $i<5 else $d-0.1,2))"); ffmpeg -v error -y -ss $ts -i "$f" -frames:v 1 -vf scale=800:-1 $t/$i.png; done
ffmpeg -v error -y -i $t/0.png -i $t/1.png -i $t/2.png -i $t/3.png -i $t/4.png -i $t/5.png -filter_complex "[0][1][2]hstack=3[a];[3][4][5]hstack=3[b];[a][b]vstack" "$o"; rm -rf $t
