#!/bin/bash

RICE=$(cat "$HOME/.config/bspwm/rice")

rofi -config "$HOME/.config/bspwm/rices/$RICE/rofi/drun.rasi" -show drun -theme-str '* { menu-title: "Apps"; }'
