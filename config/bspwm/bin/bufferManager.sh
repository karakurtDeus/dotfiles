#!/bin/bash

RICE=$(cat "$HOME/.config/bspwm/rice")

CM_LAUNCHER=rofi clipmenu -config "$HOME/.config/bspwm/rices/$RICE/rofi/drun.rasi" -p "Paste" -theme-str '* { menu-title: "Clipboard"; }'