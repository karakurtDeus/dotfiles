#!/bin/bash

RICE=$(cat "$HOME/.config/bspwm/rice")

wall_dir="$HOME/.config/bspwm/rices/$RICE/wallpapers"
prefix="main_"

shopt -s nullglob
walls=("$wall_dir"/*.{jpg,jpeg,png,webp,JPG,JPEG,PNG,WEBP})

[ ${#walls[@]} -gt 0 ] || exit 0

# Card size follows the monitor. The blur covers the whole monitor.
n=${#walls[@]}

mon_json=$(bspc query -T -m focused)
mon_rect=$(printf '%s' "$mon_json" | grep -o '"rectangle":{"x":[0-9-]*,"y":[0-9-]*,"width":[0-9]*,"height":[0-9]*}' | head -n 1)
mon_w=$(printf '%s' "$mon_rect" | sed -n 's/.*"width":\([0-9]*\),"height":\([0-9]*\).*/\1/p')
mon_h=$(printf '%s' "$mon_rect" | sed -n 's/.*"width":\([0-9]*\),"height":\([0-9]*\).*/\2/p')
[ -n "$mon_w" ] && [ -n "$mon_h" ] || { mon_w=1920; mon_h=1080; }

scale=100
while :; do
  card_h=$((mon_h * 32 * scale / 10000))
  [ "$card_h" -lt 64 ] && card_h=64
  card_w=$((card_h * 3 / 4))
  gap=$((mon_h * 36 * scale / 108000))
  [ "$gap" -lt 8 ] && gap=8
  pad=$gap
  border=$((mon_h * 4 / 1080))
  [ "$border" -lt 2 ] && border=2
  radius=$((card_w * 8 / 100))
  [ "$radius" -lt 8 ] && radius=8
  font_px=$((mon_h * 13 * scale / 108000))
  [ "$font_px" -lt 10 ] && font_px=10
  text_gap=$((mon_h * 8 * scale / 108000))
  [ "$text_gap" -lt 4 ] && text_gap=4
  text_h=$((font_px * 2))
  col_w=$((card_w + border * 2))
  row_h=$((card_h + border * 2 + text_gap + text_h))
  [ $((col_w + pad * 2)) -le "$mon_w" ] && [ "$row_h" -le $((mon_h - pad * 2)) ] && break
  scale=$((scale - 5))
  [ "$scale" -lt 40 ] && break
done

max_cols=$(( (mon_w - pad * 2 + gap) / (col_w + gap) ))
[ "$max_cols" -lt 1 ] && max_cols=1
cols=$n
[ "$cols" -gt "$max_cols" ] && cols=$max_cols

need_rows=$(( (n + cols - 1) / cols ))
max_rows=$(( (mon_h - pad * 2 + gap) / (row_h + gap) ))
[ "$max_rows" -lt 1 ] && max_rows=1
rows=$need_rows
[ "$rows" -gt "$max_rows" ] && rows=$max_rows

# rofi scales the picture so its longest side equals `size`.
# Side and top padding keep the grid at card size inside the fullscreen window.
icon_px=$card_h
thumb_w=$card_w
thumb_h=$card_h
content_w=$((cols * col_w + (cols - 1) * gap))
grid_h=$((rows * row_h + (rows - 1) * gap))
side=$(( (mon_w - content_w) / 2 ))
top=$(( (mon_h - grid_h) / 2 ))
[ "$side" -lt 0 ] && side=0
[ "$top" -lt 0 ] && top=0

thumb_dir="${XDG_CACHE_HOME:-$HOME/.cache}/bspwm/$RICE/wall-thumbs"
mkdir -p "$thumb_dir"

thumb_of() {
  local src="$1"
  local dest="$thumb_dir/$(basename "$src").${thumb_w}x${thumb_h}.png"
  if [ ! -f "$dest" ] || [ "$src" -nt "$dest" ]; then
    ffmpeg -y -loglevel error -i "$src" \
      -vf "scale=${thumb_w}:${thumb_h}:force_original_aspect_ratio=increase,crop=${thumb_w}:${thumb_h}" \
      "$dest" </dev/null || return 1
  fi
  printf '%s\n' "$dest"
}

chosen=$(
  for file in "${walls[@]}"; do
    name=$(basename "$file")
    label="${name%.*}"
    label="${label#"$prefix"}"
    thumb=$(thumb_of "$file") || thumb="$file"
    printf '%s\0icon\x1f%s\x1fdisplay\x1f%s\n' "$name" "$thumb" "$label"
  done | rofi -dmenu -i -window-title wallpaper \
    -config "$HOME/.config/bspwm/rices/$RICE/rofi/select.rasi" \
    -theme-str "window { fullscreen: true; width: ${mon_w}px; height: ${mon_h}px; border-radius: 0px; }" \
    -theme-str "* { font: \"Liberation Sans ${font_px}\"; }" \
    -theme-str "listview { columns: ${cols}; lines: ${rows}; padding: ${top}px ${side}px 0px ${side}px; spacing: ${gap}px; }" \
    -theme-str "element { spacing: ${text_gap}px; }" \
    -theme-str "element-icon { size: ${icon_px}px; border: ${border}px; border-radius: ${radius}px; }"
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
