import getpass

def return_username():
    return getpass.getuser()

from pathlib import Path
import os
import pwd
import subprocess


def cpu_name():
    for line in Path("/proc/cpuinfo").read_text().splitlines():
        if line.startswith("model name"):
            return line.split(":", 1)[1].strip()


def gpu_names():
    out = subprocess.check_output(["lspci", "-mm"], text=True)
    names = []

    for line in out.splitlines():
        fields = [part.strip('"') for part in line.split('"')[1::2]]
        if not fields:
            continue
        if "VGA" in fields[0] or "3D" in fields[0] or "Display" in fields[0]:
            device = fields[2]
            start = device.find("[")
            end = device.rfind("]")
            if start != -1 and end > start:
                device = device[start + 1:end]
            names.append(device)

    if not names:
        return "No GPU found"

    return ", ".join(names)



def kernel_version():
    return Path("/proc/sys/kernel/osrelease").read_text().strip()


def package_count():
    # pacman -Q includes repo packages and foreign ones installed with yay
    out = subprocess.check_output(["pacman", "-Qq"], text=True)
    return sum(1 for line in out.splitlines() if line.strip())

def open_kitty(command, hold=False):
    args = ["kitty"]
    if hold:
        args.append("--hold")
    args.extend(command)
    subprocess.Popen(args, start_new_session=True)

def get_current_theme():
    rice_file = os.path.expanduser("~/.config/bspwm/rice")
    if os.path.exists(rice_file):
        with open(rice_file, "r") as f:
            return f.read().strip()
    return "Unknown"


def bspwm_config_path(theme=None):
    if theme is None:
        theme = get_current_theme()
    return Path.home() / ".config/bspwm/rices" / theme / "config/bspwm"


def read_bspwm_config(theme=None):
    path = bspwm_config_path(theme)
    values = {}
    if not path.is_file():
        return values
    for line in path.read_text().splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        try:
            values[key] = int(value.strip())
        except ValueError:
            continue
    return values


def write_bspwm_config(values, theme=None):
    path = bspwm_config_path(theme)
    if not path.parent.is_dir():
        return
    path.write_text("".join(f"{key}={value}\n" for key, value in values.items()))


_bspwm = {"theme": None, "values": {}}


def current_bspwm_settings():
    theme = get_current_theme()
    if _bspwm["theme"] != theme:
        _bspwm["theme"] = theme
        _bspwm["values"] = read_bspwm_config(theme)
    return theme, _bspwm["values"]


def set_bspwm_setting(key, value):
    _bspwm["values"][key] = value
    write_bspwm_config(_bspwm["values"], _bspwm["theme"])
    subprocess.run(["bspc", "config", key, str(value)], check=False)