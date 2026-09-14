#!/bin/bash

lock="󰌾"
poweroff="󰐥"

chosen=$(
  printf '%s\n%s\n' "$lock" "$poweroff" | rofi -dmenu -i \
    -config "$HOME/.config/bspwm/rofi/select.rasi" \
    -theme-str 'listview { columns: 2; }' \
    -theme-str 'element { children: [ "element-text" ]; }' \
    -theme-str 'element-text { font: "JetBrainsMono NF 42"; vertical-align: 0.5; horizontal-align: 0.5; }'
)

case "$chosen" in
"$lock")
  "$HOME/.config/bspwm/bin/lockscreen.sh"
  ;;
"$poweroff")
  systemctl poweroff
  ;;
esac
