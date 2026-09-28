#!/bin/bash

RICE=$(cat "$HOME/.config/bspwm/rice")
rice_root="$HOME/.config/bspwm/rices"

shopt -s nullglob
dirs=("$rice_root"/*/)
[ ${#dirs[@]} -gt 0 ] || exit 0

n=${#dirs[@]}

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

icon_px=$card_h
thumb_w=$card_w
thumb_h=$card_h
content_w=$((cols * col_w + (cols - 1) * gap))
grid_h=$((rows * row_h + (rows - 1) * gap))
side=$(( (mon_w - content_w) / 2 ))
top=$(( (mon_h - grid_h) / 2 ))
[ "$side" -lt 0 ] && side=0
[ "$top" -lt 0 ] && top=0

thumb_dir="${XDG_CACHE_HOME:-$HOME/.cache}/bspwm/theme-thumbs"
mkdir -p "$thumb_dir"

preview_of() {
  local dir="$1" f
  for f in "$dir"/rice-wallpaper.*; do
    [ -f "$f" ] && printf '%s\n' "$f" && return 0
  done
  return 1
}

thumb_of() {
  local src="$1"
  local dest="$thumb_dir/$(basename "$(dirname "$src")")-$(basename "$src").${thumb_w}x${thumb_h}.png"
  if [ ! -f "$dest" ] || [ "$src" -nt "$dest" ]; then
    ffmpeg -y -loglevel error -i "$src" \
      -vf "scale=${thumb_w}:${thumb_h}:force_original_aspect_ratio=increase,crop=${thumb_w}:${thumb_h}" \
      "$dest" </dev/null || return 1
  fi
  printf '%s\n' "$dest"
}

"$HOME/.config/bspwm/bin/hideCursor.sh" &
cursor_hide=$!
trap 'kill "$cursor_hide" 2>/dev/null; wait "$cursor_hide" 2>/dev/null' EXIT

chosen=$(
  for dir in "${dirs[@]}"; do
    name=$(basename "$dir")
    src=$(preview_of "$dir") || src=""
    if [ -n "$src" ]; then
      thumb=$(thumb_of "$src") || thumb="$src"
      printf '%s\0icon\x1f%s\x1fdisplay\x1f%s\n' "$name" "$thumb" "$name"
    else
      printf '%s\n' "$name"
    fi
  done | rofi -dmenu -i -window-title theme \
    -config "$HOME/.config/bspwm/rices/$RICE/rofi/select.rasi" \
    -theme-str "window { fullscreen: true; width: ${mon_w}px; height: ${mon_h}px; border-radius: 0px; }" \
    -theme-str "* { font: \"Liberation Sans ${font_px}\"; }" \
    -theme-str "listview { columns: ${cols}; lines: ${rows}; padding: ${top}px ${side}px 0px ${side}px; spacing: ${gap}px; }" \
    -theme-str "element { spacing: ${text_gap}px; }" \
    -theme-str "element-icon { size: ${icon_px}px; border: ${border}px; border-radius: ${radius}px; }"
)
kill "$cursor_hide" 2>/dev/null
wait "$cursor_hide" 2>/dev/null
trap - EXIT

[ -n "$chosen" ] || exit 0
[ -d "$rice_root/$chosen" ] || exit 1
[ "$chosen" = "$RICE" ] && exit 0

printf '%s\n' "$chosen" > "$HOME/.config/bspwm/rice"
bspc wm -r
