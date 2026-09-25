#!/bin/bash

lock="󰌾"
logout="󰗽"
reboot="󰜉"
poweroff="󰐥"

RICE=$(cat "$HOME/.config/bspwm/rice")

mon_json=$(bspc query -T -m focused)
mon_rect=$(printf '%s' "$mon_json" | grep -o '"rectangle":{"x":[0-9-]*,"y":[0-9-]*,"width":[0-9]*,"height":[0-9]*}' | head -n 1)
mon_w=$(printf '%s' "$mon_rect" | sed -n 's/.*"width":\([0-9]*\),"height":\([0-9]*\).*/\1/p')
mon_h=$(printf '%s' "$mon_rect" | sed -n 's/.*"width":\([0-9]*\),"height":\([0-9]*\).*/\2/p')
[ -n "$mon_w" ] && [ -n "$mon_h" ] || { mon_w=1920; mon_h=1080; }

cols=4
btn=$((mon_h * 12 / 100))
[ "$btn" -lt 72 ] && btn=72
gap=$((btn * 28 / 100))
[ "$gap" -lt 16 ] && gap=16
border=$((mon_h * 4 / 1080))
[ "$border" -lt 2 ] && border=2
radius=$((btn * 18 / 100))
[ "$radius" -lt 12 ] && radius=12
font_px=$((btn * 42 / 100))
[ "$font_px" -lt 22 ] && font_px=22
text_h=$((font_px * 5 / 4))
pad_v=$(( (btn - text_h - border * 2) / 2 ))
[ "$pad_v" -lt 0 ] && pad_v=0

content_w=$((cols * btn + (cols - 1) * gap))
side=$(( (mon_w - content_w) / 2 ))
top=$(( (mon_h - btn) / 2 ))
[ "$side" -lt 0 ] && side=0
[ "$top" -lt 0 ] && top=0

chosen=$(
  printf '%s\n%s\n%s\n%s\n' "$lock" "$logout" "$reboot" "$poweroff" | rofi -dmenu -i -window-title powermenu \
    -config "$HOME/.config/bspwm/rices/$RICE/rofi/powermenu.rasi" \
    -theme-str "window { fullscreen: true; width: ${mon_w}px; height: ${mon_h}px; }" \
    -theme-str "listview { columns: ${cols}; lines: 1; spacing: ${gap}px; padding: ${top}px ${side}px 0px ${side}px; }" \
    -theme-str "element { padding: ${pad_v}px 0px; border: ${border}px; border-radius: ${radius}px; }" \
    -theme-str "element-text { font: \"JetBrainsMono NF ${font_px}\"; }"
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
