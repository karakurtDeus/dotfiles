#!/bin/bash

lock="󰌾"
logout="󰗽"
reboot="󰜉"
poweroff="󰐥"

chosen=$(
  printf '%s\n%s\n%s\n%s\n' "$lock" "$logout" "$reboot" "$poweroff" | rofi -dmenu -i \
    -config "$HOME/.config/bspwm/rofi/select.rasi" \
    -theme-str 'listview { columns: 4; }' \
    -theme-str 'element { children: [ "element-text" ]; }' \
    -theme-str 'element-text { font: "JetBrainsMono NF 42"; vertical-align: 0.5; horizontal-align: 0.5; }'
)

case "$chosen" in
"$lock")
  "$HOME/.config/bspwm/bin/lockscreen.sh"
  ;;
"$logout")
  loginctl terminate-user "$USER"
  ;;
"$reboot")
  systemctl reboot
  ;;
"$poweroff")
  systemctl poweroff
  ;;
esac
