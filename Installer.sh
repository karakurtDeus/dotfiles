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

installPkgs(){
	local -a listPkgs=("${@}")

	for pkg in "${listPkgs[@]}"; do
		if sudo pacman -Q $pkg &>> log; then
			echo "[OK] $pkg was already installed"
		else
			if sudo pacman -S $pkg --noconfirm &>> log; then
				echo "[OK] $pkg installed"
			else
				echo "[FAIL] $pkg installed"
				return 1
			fi
		fi

	done
}

systemPkgs(){
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

		# version control
		"git"
		"openssh"

		# terminal
		"kitty"

		# launcher
		"rofi"

		# bar
		"polybar"

		# WM manager and other tools
		"bspwm"
		"sxhkd"
		"xorg-server"
		"xorg-xinit"
		"xorg-xset"
	)
	installPkgs "${listPkgs[@]}"

	echo -e "\nPress any key to continue..."
	read
}

personalPkgs(){
	logo "Install personal package"

	local listPkgs=(
		"keepassxc"
		"telegram-desktop"
	)
	installPkgs "${listPkgs[@]}"

	echo -e "\nPress any key to continue..."
	read

}

main(){
	systemPkgs
	personalPkgs
	return 0
}

main
