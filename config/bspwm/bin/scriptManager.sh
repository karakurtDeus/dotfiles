#!/bin/bash

RICE=$(cat "$HOME/.config/bspwm/rice")

# name command
list=(
  Autostart  ~/.config/bspwm/bin/autostart.sh
)

[ "${#list[@]}" -eq 0 ] && exit 0

names=()
i=0
while [ "$i" -lt "${#list[@]}" ]; do
  names+=("${list[$i]}")
  i=$((i + 2))
done

chosen=$(printf '%s\n' "${names[@]}" | rofi -dmenu -i -p "Run" \
  -config "$HOME/.config/bspwm/rices/$RICE/rofi/drun.rasi" \
  -theme-str '* { menu-title: "Scripts"; }')
[ -n "$chosen" ] || exit 0

i=0
while [ "$i" -lt "${#list[@]}" ]; do
  if [ "${list[$i]}" = "$chosen" ]; then
    cmd=${list[$((i + 1))]}
    cmd=${cmd/#\~/$HOME}
    setsid $cmd >/dev/null 2>&1 &
    exit 0
  fi
  i=$((i + 2))
done
