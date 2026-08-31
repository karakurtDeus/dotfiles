#!/bin/bash

listConfigDirs=(
  "bspwm"
  "polybar"
  "sxhkd"
  "flameshot"
  "gtk-3.0"
  "gtk-4.0"
  "xdg-desktop-portal"
  "dconf"
  "dunst"
)

xinitrc=("$HOME/.xinitrc")

copyConfig() {
  if rm -R ./config &>>log; then
    echo "[OK]: rm config dir"
    if mkdir -p ./config &>>log; then
      echo "[OK] mkdir config dir"
    else
      echo "[FAIL] mkdir config dir"
      exit 1
    fi
  else
    echo "[FAIL]: rm config dir"
    exit 1
  fi

  for dir in "${listConfigDirs[@]}"; do
    if cp -R $HOME/.config/$dir &>>log; then
      echo "[OK]: $dir copy"
    else
      echo "[FAIL]: $dir copy"
      exit 1
    fi
  done

  if rm -R ./home &>>log; then
    echo "[OK]: rm home dir"
    if mkdir -p ./home &>>log; then
      echo "[OK] mkdir home dir"
    else
      echo "[FAIL] mkdir home dir"
      exit 1
    fi
  else
    echo "[FAIL]: rm home dir"
    exit 1
  fi

  if cp -R $xinitrc ./home &>>log; then
    echo "[OK] cp -R xinitrc"
  else
    echo "[FAIL] cp -R xinitrc"
    exit 1
  fi
}

updateConfig() {
  for dir in "${listConfigDirs[@]}"; do
    if rm -R $HOME/.config/$dir || true &>>log; then
      echo "[OK]: rm old $dir"
    else
      echo "[FAIL]: rm old $dir"
      exit 1
    fi
  done

  for dir in "${listConfigDirs[@]}"; do
    if cp -R ./config/$dir $HOME/.config &>>log; then
      echo "[OK]: cp new $dir"
    else
      echo "[FAIL]: cp new $dir"
      exit 1
    fi
  done

  if rm -R $xinitrc || true &>>log; then
    echo "[OK] rm old xinitrc"
    if cp -R ./home/.xinitrc $xinitrc &>>log; then
      echo "[OK] cp xinitrc"
    else
      echo "[FAIL] cp xinitrc"
      exit 1
    fi
  else
    echo "[FAIL] rm old xinitrc"
    exit 1
  fi
}

case "$1" in
--copy)
  copyConfig
  ;;
--update)
  updateConfig
  ;;
*)
  ;;
esac
