#!/bin/bash

export XDG_SESSION_TYPE=x11
export XDG_CURRENT_DESKTOP=bspwm
export XDG_SESSION_DESKTOP=bspwm
export GTK_THEME=Adwaita:dark
export QT_QPA_PLATFORMTHEME=qt5ct

dconf load / < ~/.config/dconf/interface.conf

dbus-update-activation-environment --systemd --all

xset s off 
xset -dpms

exec bspwm
