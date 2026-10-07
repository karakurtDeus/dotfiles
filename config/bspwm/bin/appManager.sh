#!/bin/bash

RICE=$(cat "$HOME/.config/bspwm/rice")
width=$(bspc config border_width)
color=$(bspc config focused_border_color)

args=(-theme-str '* { menu-title: "󰀻  Apps"; }')
if [ "$width" -gt 0 ] 2>/dev/null && [ -n "$color" ]; then
  args+=(-theme-str "window { border: ${width}px; border-color: $color; }")
fi

config="$HOME/.config/bspwm/rices/$RICE/config/rofi"
launcher=$(sed -n 's/^launcher=//p' "$config")
[ -n "$launcher" ] || launcher=drun2
icons=$(sed -n 's/^icons=//p' "$config")
case "$icons" in
  yes) show_icons=true ;;
  *) show_icons=false ;;
esac
args+=(-theme-str "configuration { show-icons: ${show_icons}; }")

rofi -config "$HOME/.config/bspwm/rices/$RICE/rofi/${launcher}.rasi" -show drun "${args[@]}"
