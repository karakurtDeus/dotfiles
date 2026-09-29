#!/bin/bash

colors_file="${XDG_CONFIG_HOME:-$HOME/.config}/polybar/colors.ini"

color() {
  awk -F '=' -v key="$1" '
    /^[[:space:]]*#/ { next }
    {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $1)
      if ($1 == key) {
        value = $2
        gsub(/[[:space:]#]/, "", value)
        print value
        exit
      }
    }
  ' "$colors_file"
}

bg=$(color lockscreen_bg)
fg=$(color lockscreen_fg)
ring=$(color lockscreen_ring)
date=$(color lockscreen_date)
verify=$(color lockscreen_verify)
wrong=$(color lockscreen_wrong)

if [ -z "$bg" ] || [ -z "$fg" ] || [ -z "$ring" ] || [ -z "$date" ] || [ -z "$verify" ] || [ -z "$wrong" ]; then
  echo "lockscreen: missing lockscreen_* color in $colors_file" >&2
  exit 1
fi

TEMP_IMAGE=/tmp/i3lock.png
picom_conf="${XDG_CONFIG_HOME:-$HOME/.config}/picom/picom.conf"

# picom dual_kawase: strength -> iterations and sample offset
strength=$(sed -n 's/^[[:space:]]*strength[[:space:]]*=[[:space:]]*\([0-9][0-9]*\).*/\1/p' "$picom_conf" | head -n 1)
passes=(1 1 2 2 2 3 3 3 3 4 4 4 4 4 4 5 5 5 5 5)
offsets=(1.25 2.25 2 3 4.25 2.5 3.25 4.25 5.5 3.25 4 5 6 7.25 8.25 4.5 5.25 6.25 7.25 8.5)
if [ -z "$strength" ] || [ "$strength" -lt 1 ] || [ "$strength" -gt ${#passes[@]} ]; then
  passes_n=3
  offset=4.25
else
  passes_n=${passes[$((strength - 1))]}
  offset=${offsets[$((strength - 1))]}
fi
# std of picom's downsample / upsample kernels at the current mip
read -r down_sigma up_sigma < <(awk -v o="$offset" 'BEGIN { printf "%.3f %.3f\n", o * sqrt(0.125), o * sqrt(1 / 3) }')

screen=$(xdpyinfo | awk '/dimensions/{print $2; exit}')
screen_w=${screen%x*}
screen_h=${screen#*x}

blur=null
for ((i = 0; i < passes_n; i++)); do
  blur+=",gblur=sigma=${down_sigma},scale=trunc(iw/2):trunc(ih/2):flags=neighbor"
done
for ((i = 0; i < passes_n; i++)); do
  blur+=",gblur=sigma=${up_sigma},scale=trunc(iw*2):trunc(ih*2):flags=bilinear"
done
blur+=",scale=${screen_w}:${screen_h}:flags=bilinear"

ffmpeg -y -loglevel quiet \
  -f x11grab -video_size "$screen" \
  -i "$DISPLAY" -vframes 1 \
  -vf "${blur},drawbox=x=0:y=0:w=iw:h=ih:color=black@0.4:t=fill" \
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
