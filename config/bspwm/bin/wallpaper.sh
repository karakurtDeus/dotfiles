#!/bin/bash

wall_dir="$HOME/.config/bspwm/pictures"
prefix="main_"

shopt -s nullglob
walls=("$wall_dir"/*.{jpg,jpeg,png,webp,JPG,JPEG,PNG,WEBP})

[ ${#walls[@]} -gt 0 ] || exit 0

cols=${#walls[@]}
[ "$cols" -gt 6 ] && cols=6

chosen=$(
  for file in "${walls[@]}"; do
    printf '%s\0icon\x1f%s\n' "$(basename "$file")" "$file"
  done | rofi -dmenu -i \
    -config "$HOME/.config/bspwm/rofi/select.rasi" \
    -theme-str "listview { columns: $cols; }"
)

[ -n "$chosen" ] || exit 0

file="$wall_dir/$chosen"
[ -f "$file" ] || exit 1

[[ "$chosen" == "$prefix"* ]] && exit 0

orig="$chosen"

free_name() {
  local ext="$1"
  local n=0
  while [ "$n" -le 19000 ]; do
    if [ ! -e "$wall_dir/$n.$ext" ] && [ ! -e "$wall_dir/${prefix}$n.$ext" ]; then
      printf '%s.%s' "$n" "$ext"
      return 0
    fi
    n=$((n + 1))
  done
  return 1
}

for current in "$wall_dir"/"$prefix"*; do
  [ -f "$current" ] || continue
  restore="$(basename "$current")"
  restore="${restore#"$prefix"}"
  dest="$wall_dir/$restore"
  if [ -e "$dest" ]; then
    ext="${restore##*.}"
    restore="$(free_name "$ext")" || exit 1
    dest="$wall_dir/$restore"
  fi
  mv "$current" "$dest"
done

target="$wall_dir/${prefix}${orig}"
if [ "$file" != "$target" ]; then
  mv "$file" "$target"
  file="$target"
fi

feh --bg-fill "$file"
bspc wm -r
