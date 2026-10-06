#!/bin/bash

RICE=$(cat "$HOME/.config/bspwm/rice")
width=$(bspc config border_width)
color=$(bspc config focused_border_color)

args=(-theme-str '* { menu-title: "󰀻  Apps"; }')
if [ "$width" -gt 0 ] 2>/dev/null && [ -n "$color" ]; then
  args+=(-theme-str "window { border: ${width}px; border-color: $color; }")
fi

launcher=$(sed -n 's/^launcher=//p' "$HOME/.config/bspwm/rices/$RICE/config/rofi")
[ -n "$launcher" ] || launcher=drun2

rofi -config "$HOME/.config/bspwm/rices/$RICE/rofi/${launcher}.rasi" -show drun "${args[@]}"
