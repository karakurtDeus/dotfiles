#!/bin/sh

# env
temp_dir="$HOME/.cache"
temp_file="$temp_dir/updates"

scan_updates() {
	local official=0
	local aur=0

	# offical
	if updates=$(checkupdates 2>/dev/null); then
		official=$(echo "$updates" | wc -l)
	fi

	# aur
	if aur_updates=$(yay -Qua 2>/dev/null); then
		aur=$(printf '%s\n' "$aur_updates" | wc -l)
	fi

	mkdir -p $temp_dir
	
	total=$((official + aur))

	echo "$total" > $temp_file
	echo "$total"
}

start_update() {
	kitty /bin/bash -c 'yay -Syu; echo; read -rp "Press Enter to close..."'
}

case "$1" in
	--scan)
		scan_updates ;;
	--update)
		start_update ;;
	*)
		;;
esac
