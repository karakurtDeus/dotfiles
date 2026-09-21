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
  "yazi"
  "kitty"
  "xfce4"
  "fontconfig"
  "picom"
)

listHomeFiles=(
  ".xinitrc"
  ".zshrc"
  ".p10k.zsh"
)

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
    if cp -R $HOME/.config/$dir ./config &>>log; then
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

  for file in "${listHomeFiles[@]}"; do
    if cp "$HOME/$file" ./home &>>log; then
      echo "[OK]: $file copy"
    else
      echo "[FAIL]: $file copy"
      exit 1
    fi
  done
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

  for file in "${listHomeFiles[@]}"; do
    if rm "$HOME/$file" || true &>>log; then
      echo "[OK]: rm old $file"
    else
      echo "[FAIL]: rm old $file"
      exit 1
    fi
  done

  for file in "${listHomeFiles[@]}"; do
    if cp "./home/$file" "$HOME/$file" &>>log; then
      echo "[OK]: cp new $file"
    else
      echo "[FAIL]: cp new $file"
      exit 1
    fi
  done
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
