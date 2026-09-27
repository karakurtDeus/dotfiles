#!/bin/sh
rice=$(cat "$HOME/.config/bspwm/rice" 2>/dev/null) || exit 0
conf=${1:-$HOME/.config/bspwm/rices/$rice/config/autostart}
[ -f "$conf" ] || exit 0

exists() {
  [ -n "$1" ] || return 1
  command -v "$1" >/dev/null 2>&1 || [ -x "$1" ]
}

browser() {
  name=$(xdg-settings get default-web-browser 2>/dev/null) || return 1
  [ -n "$name" ] || return 1
  rest=${XDG_DATA_HOME:-$HOME/.local/share}:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}
  file=
  while [ -n "$rest" ]; do
    dir=${rest%%:*}
    if [ -f "$dir/applications/$name" ]; then
      file=$dir/applications/$name
      break
    fi
    case $rest in
      *:*) rest=${rest#*:} ;;
      *) rest= ;;
    esac
  done
  [ -n "$file" ] || return 1
  cmd= class= section=0
  while IFS= read -r line; do
    case $line in
      \[*)
        section=$((section + 1))
        [ "$section" -gt 1 ] && break
        ;;
      Exec=*) [ -n "$cmd" ] || cmd=${line#Exec=} ;;
      StartupWMClass=*) class=${line#StartupWMClass=} ;;
    esac
  done < "$file"
  set -- $cmd
  bin=${1##*/}
  bin=${bin#\"}
  bin=${bin%\"}
  [ -n "$class" ] || class=$bin
  printf '%s\t%s\n' "$class" "$bin"
}

start() {
  if [ -n "${AUTOSTART_PRINT:-}" ]; then
    printf '%s\n' "$*"
    return 0
  fi
  setsid "$@" >/dev/null 2>&1 &
}

fit() {
  mon=$(bspc query -M -d "^$desk" 2>/dev/null) || return 0
  json=$(bspc query -T -m "$mon" 2>/dev/null) || return 0
  head=${json%%\"desktops\"*}
  set -- $(printf '%s\n' "$head" | sed -n 's/.*"rectangle":{"x":\(-\{0,1\}[0-9][0-9]*\),"y":\(-\{0,1\}[0-9][0-9]*\),"width":\([0-9][0-9]*\),"height":\([0-9][0-9]*\).*/\1 \2 \3 \4/p')
  [ $# -eq 4 ] || return 0
  ox=$1 oy=$2 mw=$3 mh=$4
  if [ "${sw:-0}" -gt 0 ] 2>/dev/null && [ "${sh:-0}" -gt 0 ] 2>/dev/null; then
    x=$((${x:-0} * mw / sw))
    y=$((${y:-0} * mh / sh))
    w=$((${w:-0} * mw / sw))
    h=$((${h:-0} * mh / sh))
  fi
  [ "${w:-0}" -gt "$mw" ] && w=$mw
  [ "${h:-0}" -gt "$mh" ] && h=$mh
  [ "${w:-0}" -lt 1 ] && w=1
  [ "${h:-0}" -lt 1 ] && h=1
  [ "${x:-0}" -gt $((mw - w)) ] && x=$((mw - w))
  [ "${y:-0}" -gt $((mh - h)) ] && y=$((mh - h))
  [ "${x:-0}" -lt 0 ] && x=0
  [ "${y:-0}" -lt 0 ] && y=0
  x=$((x + ox))
  y=$((y + oy))
}

place() {
  [ -n "$class" ] && [ -n "$desk" ] || return 0
  if [ "$float" = 1 ]; then
    if [ "${w:-0}" -gt 0 ] 2>/dev/null && [ "${h:-0}" -gt 0 ] 2>/dev/null; then
      fit
      bspc rule -a "$class" --one-shot desktop="^$desk" state=floating rectangle="${w}x${h}+${x:-0}+${y:-0}" || true
    else
      bspc rule -a "$class" --one-shot desktop="^$desk" state=floating || true
    fi
  else
    bspc rule -a "$class" --one-shot desktop="^$desk" state=tiled || true
  fi
}

work=$(mktemp -d)
claims=$work/claims
mkdir -p "$claims"
trap 'rm -rf "$work"' EXIT

class_of() {
  bspc query -T -n "$1" 2>/dev/null | sed -n 's/.*"className":"\([^"]*\)".*/\1/p' | head -n 1
}

watch() {
  want=$1 desk=$2 float=$3 x=$4 y=$5 w=$6 h=$7 snap=$8 ticks=$9
  mine=$(mktemp "$work/mine.XXXXXX") || return 0
  held= stable=0 i=0
  while [ "$i" -lt "$ticks" ]; do
    i=$((i + 1))
    fresh=0
    for id in $(bspc query -N -n .window 2>/dev/null); do
      grep -qx "$id" "$snap" 2>/dev/null && continue
      grep -qx "$id" "$mine" 2>/dev/null && continue
      [ "$(class_of "$id")" = "$want" ] || continue
      printf '%s\n' "$id" >> "$mine"
      mkdir "$claims/$id" 2>/dev/null || true
      fresh=1
    done
    current=
    while IFS= read -r id; do
      [ -n "$id" ] || continue
      bspc query -N -n "$id" >/dev/null 2>&1 || continue
      current=$id
      cur=$(bspc query -D -n "$id" 2>/dev/null) || continue
      goal=$(bspc query -D -d "^$desk" 2>/dev/null) || continue
      if [ "$cur" != "$goal" ]; then
        bspc node "$id" -d "^$desk" || true
        fresh=1
      fi
      if [ "$float" = 1 ]; then
        bspc node "$id" -t floating || true
        if [ "${w:-0}" -gt 0 ] 2>/dev/null && [ "${h:-0}" -gt 0 ] 2>/dev/null && command -v xdotool >/dev/null 2>&1; then
          xdotool windowsize "$id" "$w" "$h" windowmove "$id" "$x" "$y" || true
        fi
      fi
    done < "$mine"
    if [ -n "$current" ] && [ "$fresh" = 0 ] && [ "$current" = "$held" ]; then
      stable=$((stable + 1))
      [ "$stable" -ge 3 ] && break
    else
      held=$current
      stable=0
    fi
    sleep 0.4
  done
  rm -f "$snap" "$mine"
}

run() {
  snap=$(mktemp "$work/snap.XXXXXX") || return 0
  bspc query -N -n .window > "$snap" 2>/dev/null || true
  if [ -n "${AUTOSTART_PRINT:-}" ] || [ -z "$desk" ]; then
    start "$@"
    return 0
  fi
  place
  start "$@"
  watch "$class" "$desk" "$float" "$x" "$y" "$w" "$h" "$snap" 50
  if [ -n "$url" ]; then
    sleep 1
  fi
}

while IFS=$(printf '\t') read -r class exec url desk float x y w h sw sh title; do
  case $class in \#*) continue ;; esac
  [ "$class" = - ] && class=
  [ "$exec" = - ] && exec=
  [ "$url" = - ] && url=
  [ "$title" = - ] && title=
  if [ -z "$url" ] && [ "$exec" = firefox ] && [ -n "$title" ]; then
    url=$(PYTHONPATH="$HOME/.config/bspwm/bin/core" python3 -c 'import sys, control_panel; print(control_panel.firefox_url(sys.argv[1]))' "$title" 2>/dev/null) || url=
  fi
  [ -n "$class$exec$url" ] || continue
  case $desk in ''|*[!0-9]*) desk= ;; esac
  if [ -n "$desk" ]; then
    count=$(bspc query -D 2>/dev/null | wc -l)
    [ "${count:-0}" -gt 0 ] && [ "$desk" -gt "$count" ] && desk=$count
  fi
  if [ -n "$url" ]; then
    info=$(browser) || continue
    class=${info%%	*}
    bin=${info#*	}
    exists "$bin" || continue
    run "$bin" --new-window "$url"
    continue
  fi
  exists "$exec" || continue
  run "$exec"
done < "$conf"
