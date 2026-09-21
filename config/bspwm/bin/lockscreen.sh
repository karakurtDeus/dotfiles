#!/bin/bash

bg=000000ff
fg=C5C8C6ff
ring=F0C674ff
date=F0C674ff
verify=9ece6aff
wrong=f7768eff

TEMP_IMAGE=/tmp/i3lock.png

ffmpeg -y -loglevel quiet \
  -f x11grab -video_size "$(xdpyinfo | awk '/dimensions/{print $2}')" \
  -i "$DISPLAY" -vframes 1 \
  -vf "gblur=sigma=20" \
  "$TEMP_IMAGE"

i3lock -n --force-clock -i "$TEMP_IMAGE" --fill -e --indicator \
  --radius=80 --ring-width=8 \
  --inside-color=$bg --ring-color=$ring \
  --insidever-color=$bg --ringver-color=$verify \
  --insidewrong-color=$bg --ringwrong-color=$wrong \
  --keyhl-color=$fg --separator-color=$bg --bshl-color=$wrong \
  --time-str="%H:%M" --time-size=140 --date-str="%a, %d %b" --date-size=45 \
  --verif-text="Verifying Password..." --wrong-text="Wrong Password!" \
  --noinput-text="" --greeter-text="" \
  --ind-pos="w/2:h/2+70" \
  --time-pos="w/2:iy-180" --date-pos="tx:ty+60" \
  --verif-pos="w/2:iy+120" --wrong-pos="w/2:iy+120" \
  --time-align=0 --date-align=0 --verif-align=0 --wrong-align=0 \
  --time-font="JetBrainsMono NF:style=Bold" --date-font="JetBrainsMono NF" \
  --verif-font="JetBrainsMono NF" --wrong-font="JetBrainsMono NF" \
  --verif-size=23 --wrong-size=23 \
  --time-color=$date --date-color=$date \
  --verif-color=$verify --wrong-color=$wrong \
  --pointer=default \
  --pass-media-keys --pass-volume-keys
