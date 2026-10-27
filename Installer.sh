#!/bin/bash

logo() {
  echo ""
  #clear
  local -a describe=$1

  if [[ -n "$1" ]]; then
    echo -e "$describe\n"
  else
    echo -e "\n"
  fi

  return 0
}

create_std_dir() {
  local listDirs=(
    "Documents"
    "Downloads"
    "Music"
    "Pictures"
    "Videos"
    "Projects"
  )

  for dir in "${listDirs[@]}"; do
    mkdir -p $HOME/$dir &>>log
  done

  return 0
}

installPkgs() {
  local -a listPkgs=("${@}")

  for pkg in "${listPkgs[@]}"; do
    if sudo pacman -Q $pkg &>>log; then
      echo "[OK] $pkg was already installed"
    else
      if sudo pacman -S $pkg --noconfirm &>>log; then
        echo "[OK] $pkg installed"
      else
        echo "[FAIL] $pkg installed"
        exit 1
      fi
    fi

  done

  return 0
}

install_yay_pkgs() {
  local -a listPkgs=("${@}")

  for pkg in "${listPkgs[@]}"; do
    if yay -Q $pkg &>>log; then
      echo "[OK] $pkg was already installed"
    else
      if yay -S $pkg --noconfirm &>>log; then
        echo "[OK] $pkg installed"
      else
        echo "[FAIL] $pkg installed"
        exit 1
      fi
    fi

  done

  return 0
}

system_pkgs() {
  logo "Install system package"

  local listPkgs=(
    # fonts
    "noto-fonts"
    "noto-fonts-cjk"
    "noto-fonts-emoji"
    "ttf-dejavu"
    "ttf-liberation"
    "ttf-jetbrains-mono-nerd"
    "ttf-font-awesome"
    "ttf-nerd-fonts-symbols"

    # browser
    "firefox"

    # code editor
    "vim"
    "neovim"

    # version control / build
    "git"
    "openssh"
    "base-devel"

    # terminal
    "kitty"

    # file manager
    "thunar"
    "gvfs"
    "gvfs-smb"

    # launcher
    "rofi"

    # web utils
    "wget"

    # screen shot
    "flameshot"

    # network
    "networkmanager" # for nmtui and other

    # multimedia
    "pipewire"
    "wireplumber"
    "pipewire-pulse"
    "pipewire-alsa"

    # copy / paste
    "xclip"
    "xsel"
    "clipmenu"
    "clipnotify"

    # shell
    "btop"
    "zsh"
    "zsh-completions"
    "eza"
    "bat"
    "fzf"
    "yazi"
    "ffmpeg"
    "p7zip"
    "jq"
    "poppler"
    "fd"
    "ripgrep"

    # firewall
    "ufw"

    # bar
    "polybar"

    # git
    "git"
    "less"

    # notification
    "dunst"

    # bluetooth
    "bluez"
    "bluez-utils"
    "bluetui"

    # desktop portal
    "xdg-desktop-portal"
    "xdg-desktop-portal-gtk"

    # lockscreen
    "xorg-xdpyinfo"

    # network tools
    "rsync"
    "nethogs" #> program connect net scan
    "nmap"    #> port scan
    "mtr"     #> traceroute && ping
    "iftop"   #> traffic connects, example: iftop -i enp3s0f3u1 -n -P
    "bind"    #> dig && nslookup
    "tcpdump"

    # WM manager and other tools
    "bspwm"
    "xorg-xsetroot"
    "pacman-contrib"
    "picom"
    "sxhkd"
    "xorg-server"
    "xorg-xinit"
    "xorg-xset"
    "feh" # background
    # just need xd
    #"cmatrix"
    #"cava"
    #"playerctl"
  )
  installPkgs "${listPkgs[@]}"

  return 0
}

enable_multilib() {
  logo "Enable multilib"

  if grep -q '^\[multilib\]' /etc/pacman.conf; then
    echo "[OK] multilib"
  else
    if sudo sed -i '/^#\[multilib\]/,/^#Include = \/etc\/pacman\.d\/mirrorlist/s/^#//' /etc/pacman.conf; then
      echo "[OK] add multilib"
    else
      echo "[FAIL] add multilib"
    fi
  fi

  if sudo pacman -Syu --noconfirm &>>log; then
    echo "[OK] update pkg"
  else
    echo "[FAIL] update pkg"
    exit 1
  fi

  return 0
}

input_value() {
  local question=$1
  read -rp "$question" value

  case $value in
  "y" | "yes" | "YES" | "Yes")
    echo "1"
    ;;
  *)
    echo "0"
    ;;
  esac
  return
}

personal_pkgs() {
  local optional=$1

  if [[ $optional == 1 ]]; then
    logo "Install personal package"
    local listPkgs=(
      "keepassxc"
      "telegram-desktop"
      "obsidian"
      "discord"
      "anki"
      "espeak-ng"
      "speech-dispatcher"
      "signal-desktop"
      #"kdenlive"
      "wireguard-tools"
      "mpv"
      "steam"
      #"obs-studio"
      "krita"
    )
    installPkgs "${listPkgs[@]}"
    local listPkgs=(
      "cursor-bin"
      "spotify"
      "winbox"
    )
    install_yay_pkgs "${listPkgs[@]}"
  fi

  return 0
}

start_services() {
  logo "Enable and start services"

  local -a services=(
    "NetworkManager"
    "bluetooth"
  )

  for src in "${services[@]}"; do
    if sudo systemctl enable --now $src &>>log; then
      echo "[OK] Enable and start service $src"
    else
      echo "[FAIL] Enable and start service $src"
    fi

  done

  return 0
}

install_fonts() {
  logo "Fonts install"

  local coreDir="$HOME/.local/share/fonts"

  local fontMesloLGS=(
    "MesloLGS-NF"
    "https://raw.githubusercontent.com/romkatv/powerlevel10k-media/master/MesloLGS%20NF%20Regular.ttf"
    "https://raw.githubusercontent.com/romkatv/powerlevel10k-media/master/MesloLGS%20NF%20Bold.ttf"
    "https://raw.githubusercontent.com/romkatv/powerlevel10k-media/master/MesloLGS%20NF%20Italic.ttf"
    "https://raw.githubusercontent.com/romkatv/powerlevel10k-media/master/MesloLGS%20NF%20Bold%20Italic.ttf"
  )

  if mkdir -p $coreDir &>>log; then
    echo "[OK] Font core dir create"
  else
    echo "[FAIL] Font core dir create"
    exit 1
  fi

  # font 0
  if fc-list | grep -qi "MesloLGS NF"; then
    echo "[OK] MesloLGS NF already installed"
  else
    mkdir -p "$coreDir/${fontMesloLGS[0]}"
    for font in "${fontMesloLGS[@]:1}"; do
      if wget -P "$coreDir/${fontMesloLGS[0]}" "$font" &>>log; then
        echo "[OK] $font"
      else
        echo "[FAIL] $font"
        exit 1
      fi
    done
  fi

  # font 1
  local fontPressStart2P=(
    "PressStart2P"
    "https://raw.githubusercontent.com/google/fonts/main/ofl/pressstart2p/PressStart2P-Regular.ttf"
  )

  if fc-list | grep -qi "Press Start 2P"; then
    echo "[OK] Press Start 2P already installed"
  else
    mkdir -p "$coreDir/${fontPressStart2P[0]}"
    if wget -P "$coreDir/${fontPressStart2P[0]}" "${fontPressStart2P[1]}" &>>log; then
      echo "[OK] Press Start 2P"
    else
      echo "[FAIL] Press Start 2P"
      exit 1
    fi
  fi

  # finish
  if fc-cache -fv &>>log; then
    echo "[OK] Font cache updated"
  else
    echo "[FAIL] Font cache update"
    exit 1
  fi

  return 0
}

nvidia_pkgs() {
  local optional=$1

  if [[ $optional == 1 ]]; then
    logo "Install nvidia package"
    local listPkgs=(
      "linux-headers"
      "nvidia-dkms"
      "nvidia-utils"
      "lib32-nvidia-utils"
    )
    installPkgs "${listPkgs[@]}"
  fi

  return 0
}

install_yay() {
  logo "Install yay"

  local temp_dir="/tmp/yay"

  if pacman -Q yay &>/dev/null; then
    echo "[OK] pkg yay is installed"

    return
  fi

  rm -rf "$temp_dir"

  if git clone https://aur.archlinux.org/yay.git "$temp_dir" &>>log; then
    echo "[OK] clone yay"
  else
    echo "[FAIL] clone yay"
    exit 1
  fi

  if (
    cd "$temp_dir" || exit 1
    makepkg -si --noconfirm
  ) &>>log; then
    echo "[OK] build yay"
  else
    echo "[FAIL] build yay"
    exit 1
  fi

  rm -rf "$temp_dir"

  return 0
}

install_yay_pkgs_std() {
  logo "Yay std pkgs"

  listPkgs=(
    "i3lock-color"
    "qogir-cursor-theme"
  )
  install_yay_pkgs "${listPkgs[@]}"

  return 0
}

zsh_config() {
  logo "ZSH config"

  if sudo chsh -s /bin/zsh "$USER" >/dev/null 2>&1; then
    echo "[OK] zsh set as default shell"
  else
    echo "[FAIL] zsh set as default shell"
  fi

  if mkdir -p "$HOME/.config/zsh/plugins" &>>log; then
    echo "[OK] zsh directory created"
  else
    echo "[FAIL] zsh directory created"
  fi

  local repos=(
    "https://github.com/zsh-users/zsh-autosuggestions.git|plugins/zsh-autosuggestions"
    "https://github.com/zsh-users/zsh-syntax-highlighting.git|plugins/zsh-syntax-highlighting"
    "https://github.com/romkatv/powerlevel10k.git|powerlevel10k"
  )

  for item in "${repos[@]}"; do
    repo="${item%%|*}"
    target="${item##*|}"
    dest="$HOME/.config/zsh/$target"

    if [ -d "$dest/.git" ]; then
      echo "[OK] $target already exists"
      continue
    fi

    if git clone "$repo" "$dest" &>>log; then
      echo "[OK] $target cloned"
    else
      echo "[FAIL] clone $repo"
    fi
  done

  local dir
  dir="$(dirname "$(realpath "$0")")"

  local shellFiles=(
    ".zshrc"
    ".p10k.zsh"
  )

  for file in "${shellFiles[@]}"; do
    if rm "$HOME/$file" >/dev/null 2>&1; then
      echo "[OK] rm old $file"
    else
      echo "[OK] old $file empty"
    fi

    if cp "$dir/home/$file" "$HOME/$file"; then
      echo "[OK] paste $file"
    else
      echo "[FAIL] paste $file"
    fi
  done

  return 0
}

install_lazyvim() {
  logo "Install LazyVim"

  local nvim_dir="$HOME/.config/nvim"

  if [ -d "$nvim_dir" ]; then
    echo "[OK] LazyVim already installed"
  else
    if git clone https://github.com/LazyVim/starter.git "$nvim_dir" >/dev/null 2>&1; then
      rm -rf "$nvim_dir/.git"
      echo "[OK] install LazyVim"
    else
      echo "[FAIL] install LazyVim"
    fi
  fi

  if cat >"$nvim_dir/lua/plugins/snacks.lua" <<'EOF'
return {
  "folke/snacks.nvim",
  opts = {
    picker = {
      sources = {
        explorer = { hidden = true },
        files = { hidden = true },
      },
    },
  },
}
EOF
  then
    echo "[OK] snacks hidden files"
  else
    echo "[FAIL] snacks hidden files"
  fi

  local lazyvim_json="$nvim_dir/lazyvim.json"

  if [ -f "$lazyvim_json" ] && jq --arg extra "lazyvim.plugins.extras.util.mini-hipatterns" '
      .extras += [$extra]
      | .extras |= unique
    ' "$lazyvim_json" >"$lazyvim_json.tmp" && mv "$lazyvim_json.tmp" "$lazyvim_json"; then
    echo "[OK] lazyvim extra mini-hipatterns"
  else
    echo "[FAIL] lazyvim extra mini-hipatterns"
  fi

  return 0
}

ufw_config() {
  logo "UFW config"

  if sudo ufw default deny incoming >/dev/null 2>&1; then
    printf "[OK] ufw rule deny incoming\n"
  else
    printf "[FAIL] ufw rule deny incoming\n"
    exit 1
  fi

  if sudo ufw default allow outgoing >/dev/null 2>&1; then
    printf "[OK] ufw rule allow outgoing\n"
  else
    printf "[FAIL] ufw rule allow outgoing\n"
    exit 1
  fi

  enable_output=$(sudo ufw --force enable 2>&1) || enable_status=$?
  enable_status=${enable_status:-0}

  if [ "$enable_status" -eq 0 ]; then
    printf "[OK] ufw enabled\n"
  else
    printf "[FAIL] ufw enable\n"
    [ -n "$enable_output" ] && printf "%s\n" "$enable_output"
  fi

  if sudo systemctl enable ufw.service >/dev/null 2>&1; then
    printf "[OK] ufw service enabled\n"
  else
    printf "[FAIL] ufw service enable\n"
  fi

  return 0
}

main() {
  local personal_pkgs=$(input_value "Do you want install karakurt pks? (y/n): ")
  local nvidia_drivers=$(input_value "Do you want install nvidia drivers? (y/n): ")

  create_std_dir
  system_pkgs
  enable_multilib
  install_yay
  install_yay_pkgs_std
  personal_pkgs $personal_pkgs
  start_services
  install_fonts
  nvidia_pkgs $nvidia_drivers
  zsh_config
  install_lazyvim
  ufw_config
  exit 0
}

main
