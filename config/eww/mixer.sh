#!/bin/sh
wpctl status | awk '
  function flush() {
    if (id == "" || !play) return
    cmd = "wpctl inspect " id
    while ((cmd | getline line) > 0)
      if (index(line, "application.process.binary")) {
        sub(/^[^\"]*\"/, "", line)
        sub(/\".*$/, "", line)
        if (line != "") name = line
      }
    close(cmd)
    cmd = "wpctl get-volume " id
    pct = 0
    if ((cmd | getline vol) > 0 && match(vol, /[0-9.]+/))
      pct = int(substr(vol, RSTART, RLENGTH) * 100)
    close(cmd)
    printf "(box :hexpand true :space-evenly false :spacing 8 (label :width 150 :halign \"start\" :text \"%s\") (scale :min 0 :max 100 :hexpand true :value %d :onchange \"wpctl set-volume %s {}%%\"))\n", name, pct, id
    id = ""
    play = 0
  }
  /Streams:/ { on = 1; next }
  on && /^Video/ { flush(); exit }
  on && /^[ \t]*[0-9]+\./ {
    title = $0
    sub(/^[ \t]*[0-9]+\.[ \t]*/, "", title)
    sub(/[ \t]+$/, "", title)
    if (title ~ /output_|input_|monitor_/) {
      if (title ~ /^output_/) play = 1
      next
    }
    flush()
    id = $1
    sub(/\./, "", id)
    name = title
    gsub(/["\\]/, "", name)
    play = 0
  }
  END { flush() }
' | {
  printf '(box :orientation "v" :spacing 6 :space-evenly false :hexpand true '
  cat
  printf ')'
}
