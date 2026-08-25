#!/bin/bash

logo() {
	clear

	local -a describe=$1

	if [[ -n "$1" ]]; then
		echo -e "$describe\n"
	else
		echo -e "\n"
	fi
}

createStdDir(){
	local listDirs=(
		"Documents"
		"Downloads"
		"Music"
		"Pictures"
		"Videos"
		"Projects"
	)

	for dir in "${listDirs[@]}"; do
		mkdir -p $HOME/$dir &>> log
	done

}

installPkgs(){
	local -a listPkgs=("${@}")

	for pkg in "${listPkgs[@]}"; do
		if sudo pacman -Q $pkg &>> log; then
			echo "[OK]: $pkg was already installed"
		else
			if sudo pacman -S $pkg --noconfirm &>> log; then
				echo "[OK]: $pkg installed"
			else
				echo "[FAIL]: $pkg installed"
				exit 1
			fi
		fi

	done
}

systemPkgs(){
	logo "Install system package"

	if sudo pacman -Syu &>> log; then
		echo "[OK]: update pkg"
	else
		echo "[FAIL]: update pkg"
		exit 1
	fi

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

		# version control
		"git"
		"openssh"

		# terminal
		"kitty"

		# file manager
		"thunar"

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

		# benchmark
		"btop"

		# bar
		"polybar"

		# notification
		"dunst"

		# WM manager and other tools
		"bspwm"
		"sxhkd"
		"xorg-server"
		"xorg-xinit"
		"xorg-xset"
		"feh"         # background
	)
	installPkgs "${listPkgs[@]}"

	echo -e "\nPress any key to continue..."
	read
}

enableMultilib() {
	logo "Enable multilib"

	if grep -q '^\[multilib\]' /etc/pacman.conf; then
		echo "[OK]: multilib"
	else
		if sudo sed -i '/^#\[multilib\]/,/^#Include = \/etc\/pacman\.d\/mirrorlist/s/^#//' /etc/pacman.conf; then
			echo "[OK]: add multilib"
		else
			echo "[FAIL]: add multilib"
		fi
	fi

	if sudo pacman -Syu &>> log; then
		echo "[OK]: update pkg"
	else
		echo "[FAIL]: update pkg"
		exit 1
	fi

	echo -e "\nPress any key to continue..."
	read
}

personalPkgs(){
	logo "Install personal package"

	read -r -p "Install karakurt personal package (y/n)? "  answer

	case $answer in 
		"y" | "yes" | "YES" | "Y")

			local listPkgs=(
				"keepassxc"
				"telegram-desktop"
				"discord"
			)
			installPkgs "${listPkgs[@]}"
			;;
		*)
			;;
	esac

	echo -e "\nPress any key to continue..."
	read

}


startServices() {
	logo "Enable and start services"

	local -a services=(
		"NetworkManager"
	)

	for src in "${services[@]}"; do
		if sudo systemctl enable --now $src &>> log; then
			echo "[OK]: Enable and start service $src"
		else
			echo "[FAIL]: Enable and start service $src"
		fi

	done

	echo -e "\nPress any key to continue..."
	read
}


installFonts() {
	logo "Fonts install"

	local coreDir="$HOME/.local/share/fonts"

	local fontMesloLGS=(
		"MesloLGS-NF"
		"https://raw.githubusercontent.com/romkatv/powerlevel10k-media/master/MesloLGS%20NF%20Regular.ttf"
		"https://raw.githubusercontent.com/romkatv/powerlevel10k-media/master/MesloLGS%20NF%20Bold.ttf"
		"https://raw.githubusercontent.com/romkatv/powerlevel10k-media/master/MesloLGS%20NF%20Italic.ttf" 
		"https://raw.githubusercontent.com/romkatv/powerlevel10k-media/master/MesloLGS%20NF%20Bold%20Italic.ttf"
	)


	if mkdir -p $coreDir &>> log; then
		echo "[OK]: Font core dir create"
	else
		echo "[FAIL]: Font core dir create"
		exit 1
	fi

	# font 0
	if fc-list | grep -qi "MesloLGS NF"; then
		echo "[OK]: MesloLGS NF already installed"
   	else
		mkdir -p "$coreDir/${fontMesloLGS[0]}"
		for font in "${fontMesloLGS[@]:1}"; do
    			if wget -P "$coreDir/${fontMesloLGS[0]}" "$font" &>> log; then
       	 			echo "[OK]: $font"
    			else
        			echo "[FAIL]: $font"
				exit 1
    			fi
		done
	fi

	# finish
    	if fc-cache -fv &>> log; then
        	echo "[OK]: Font cache updated"
    	else
        	echo "[FAIL]: Font cache update"
        	exit 1
    	fi

	echo -e "\nPress any key to continue..."
	read
}

nvidiaPkgs() {
	logo "Install nvidia package"

	read -r -p "Do you have an Nvidia gpu (y/n)? "  answer

	case $answer in
		"y" | "yes" | "YES" | "Y")
			local listPkgs=(
				"linux-headers"
				"nvidia-dkms"
				"nvidia-utils"
				"lib32-nvidia-utils"
			)
			installPkgs "${listPkgs[@]}"
			;;
		*)
			;;
	esac

	echo -e "\nPress any key to continue..."
	read
}

main(){
	createStdDir
	systemPkgs
	enableMultilib
	personalPkgs
	startServices
	installFonts
	nvidiaPkgs
	exit 0
}

main
