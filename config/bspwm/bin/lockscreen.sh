#!/bin/bash

bg=1a1b26ff
fg=c0caf5ff
ring=15161eff
wrong=f7768eff
date=c0caf5ff
verify=9ece6aff

TEMP_IMAGE=/tmp/i3lock.png

ffmpeg -y -loglevel quiet \
  -f x11grab -video_size "$(xdpyinfo | awk '/dimensions/{print $2}')" \
  -i "$DISPLAY" -vframes 1 \
  -vf "gblur=sigma=20" \
  "$TEMP_IMAGE"

i3lock -n --force-clock -i "$TEMP_IMAGE" --fill -e --indicator \
  --radius=30 --ring-width=60 --inside-color=$bg \
  --ring-color=$ring --insidever-color=$verify --ringver-color=$verify \
  --insidewrong-color=$wrong --ringwrong-color=$wrong --line-uses-inside \
  --keyhl-color=$verify --separator-color=$verify --bshl-color=$verify \
  --time-str="%H:%M" --time-size=140 --date-str="%a, %d %b" \
  --date-size=45 --verif-text="Verifying Password..." --wrong-text="Wrong Password!" \
  --noinput-text="" --greeter-text="Type the password to Unlock" --ind-pos="300:610" \
  --time-font="JetBrainsMono NF:style=Bold" --date-font="JetBrainsMono NF" --verif-font="JetBrainsMono NF" \
  --greeter-font="JetBrainsMono NF" --wrong-font="JetBrainsMono NF" --verif-size=23 \
  --greeter-size=23 --wrong-size=23 --time-pos="300:390" \
  --date-pos="300:450" --greeter-pos="300:780" --wrong-pos="300:820" \
  --verif-pos="300:820" --date-color=$date --time-color=$date \
  --greeter-color=$fg --wrong-color=$wrong --verif-color=$verify \
  --pointer=default \
  --pass-media-keys --pass-volume-keys
