#!/bin/bash

rm -R config
mkdir config

cp -R ~/.config/bspwm config
cp -R ~/.config/polybar config
cp -R ~/.config/sxhkd config
cp -R ~/.config/flameshot config
cp -R ~/.config/gtk-3.0 config
cp -R ~/.config/gtk-4.0 config
cp -R ~/.config/xdg-desktop-portal config
cp -R ~/.config/dconf config

rm -R home
mkdir home

cp -R ~/.xinitrc home
