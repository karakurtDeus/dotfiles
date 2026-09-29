import ctypes
import getpass

def return_username():
    return getpass.getuser()

from pathlib import Path
import json
import os
import pwd
import re
import subprocess
import tempfile
import time


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


def backlight_path():
    root = Path("/sys/class/backlight")
    if not root.is_dir():
        return None
    for path in sorted(root.iterdir()):
        if (path / "brightness").is_file() and (path / "max_brightness").is_file():
            return path
    return None


def _percent(current, total):
    if total <= 0:
        return 0
    return min(100, max(0, round(current * 100 / total)))


def read_brightness():
    path = backlight_path()
    if path is None:
        return None
    try:
        current = int((path / "brightness").read_text())
        maximum = int((path / "max_brightness").read_text())
    except (OSError, ValueError):
        return None
    return _percent(current, maximum)


def set_brightness(percent):
    path = backlight_path()
    if path is None:
        return
    try:
        maximum = int((path / "max_brightness").read_text())
    except (OSError, ValueError):
        return
    value = min(maximum, max(1, round(int(percent) * maximum / 100)))
    subprocess.run(
        [
            "busctl", "call",
            "org.freedesktop.login1",
            "/org/freedesktop/login1/session/auto",
            "org.freedesktop.login1.Session",
            "SetBrightness",
            "ssu", "backlight", path.name, str(value),
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _wpctl(*args):
    try:
        return subprocess.check_output(
            ["wpctl", *args],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""


def _parse_volume(text):
    muted = "[MUTED]" in text
    volume = 0.0
    for token in text.split():
        try:
            volume = float(token)
            break
        except ValueError:
            continue
    return min(100, max(0, round(volume * 100))), muted


def read_audio():
    sink_volume, sink_mute = _parse_volume(_wpctl("get-volume", "@DEFAULT_AUDIO_SINK@"))
    _source_volume, source_mute = _parse_volume(_wpctl("get-volume", "@DEFAULT_AUDIO_SOURCE@"))
    return {
        "volume": sink_volume,
        "sink_mute": sink_mute,
        "source_mute": source_mute,
    }


def set_volume(percent):
    level = min(100, max(0, int(percent)))
    subprocess.run(
        ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "0"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{level}%"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def set_muted(target, muted):
    node = "@DEFAULT_AUDIO_SINK@" if target == "sink" else "@DEFAULT_AUDIO_SOURCE@"
    subprocess.run(
        ["wpctl", "set-mute", node, "1" if muted else "0"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

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


PICOM_CONF = Path.home() / ".config/picom/picom.conf"
_PICOM_ANIMATIONS = """# picom-panel-animations
animations = ({
  triggers = ["open", "show"];
  preset = "slide-in";
  duration = 0.2;
}, {
  triggers = ["close", "hide"];
  preset = "slide-out";
  duration = 0.2;
});
# /picom-panel-animations
"""
_SQUARE_MATCH = (
    "class_g = 'Polybar' || class_g = 'Dunst' || "
    "(class_g = 'Rofi' && (name = 'rofi - wallpaper' || name = 'rofi - powermenu' || name = 'rofi - theme'))"
)
_SQUARE_RULE = f"""  {{
    match = "{_SQUARE_MATCH}";
    corner-radius = 0;
  }},
"""
_picom = {"values": None, "apps": None}
_OPACITY_BLOCK = re.compile(r"\n?# picom-panel-opacity\n.*?# /picom-panel-opacity\n?", re.S)


def _picom_scalar(text, key):
    match = re.search(rf"(?m)^{re.escape(key)}\s*=\s*([^;\n]*);", text)
    return match.group(1).strip() if match else None


def _set_picom_scalar(text, key, value):
    line = f"{key} = {value};"
    pattern = rf"(?m)^{re.escape(key)}\s*=\s*[^;\n]*;"
    if re.search(pattern, text):
        return re.sub(pattern, line, text, count=1)
    if text and not text.endswith("\n"):
        text += "\n"
    return text + line + "\n"


def read_picom_settings():
    text = PICOM_CONF.read_text() if PICOM_CONF.is_file() else ""
    fading = _picom_scalar(text, "fading") == "true"
    step = _picom_scalar(text, "fade-in-step") or "0.03"
    try:
        fade = int(round(float(step) * 100)) if fading else 0
    except ValueError:
        fade = 3 if fading else 0
    color = (_picom_scalar(text, "shadow-color") or '"#000000"').strip().strip('"')
    radius = _picom_scalar(text, "corner-radius") or "0"
    catchall = re.search(r"\{\s*blur-background\s*=\s*false\s*;", text)
    return {
        "corner_radius": int(radius) if radius.isdigit() else 0,
        "shadow": _picom_scalar(text, "shadow") == "true",
        "shadow_color": color if color.startswith("#") else "#000000",
        "fading": min(100, max(0, fade)),
        "blur": _picom_scalar(text, "blur-background") == "true" and not catchall,
        "animations": "# picom-panel-animations" in text,
        "backend": (_picom_scalar(text, "backend") or '"glx"').strip().strip('"'),
        "vsync": _picom_scalar(text, "vsync") != "false",
        **_read_opacity(text),
    }


def _read_opacity(text):
    match = _OPACITY_BLOCK.search(text)
    body = match.group(0) if match else ""
    amount = 80
    amount_match = re.search(r"(?m)^# amount = (\d+);", body)
    if amount_match:
        amount = int(amount_match.group(1))
    exclude = re.findall(r"(?m)^# exclude = (.+);", body)
    enabled = bool(re.search(r"(?m)^# enabled = true;", body))
    return {
        "opacity_enabled": enabled,
        "opacity": min(100, max(15, amount)),
        "opacity_exclude": exclude,
    }


def system_apps():
    if _picom["apps"] is None:
        apps = {}
        data_home = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))
        data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":")
        for base in [data_home, *data_dirs]:
            directory = Path(base) / "applications"
            if not directory.is_dir():
                continue
            for path in directory.glob("*.desktop"):
                name = wm_class = exec_name = None
                hidden = False
                for line in path.read_text(errors="replace").splitlines():
                    if line.startswith("["):
                        if line.strip() != "[Desktop Entry]":
                            break
                        continue
                    if line.startswith("Name=") and name is None:
                        name = line.split("=", 1)[1].strip()
                    elif line.startswith("StartupWMClass="):
                        wm_class = line.split("=", 1)[1].strip()
                    elif line.startswith("Exec=") and exec_name is None:
                        parts = [part for part in line.split("=", 1)[1].split() if not part.startswith("%")]
                        if parts:
                            exec_name = Path(parts[0]).name
                    elif line in ("NoDisplay=true", "Hidden=true"):
                        hidden = True
                if hidden or not name:
                    continue
                klass = wm_class or (name if " " not in name else exec_name)
                if klass:
                    apps.setdefault(klass, name)
        for klass, name in (("Polybar", "Polybar"), ("Dunst", "Dunst"), ("Rofi", "Rofi")):
            apps.setdefault(klass, name)
        _picom["apps"] = sorted(
            ((name if name == klass else f"{name} ({klass})", klass) for klass, name in apps.items()),
            key=lambda item: item[0].casefold(),
        )
    return _picom["apps"]


def _class_match(klass):
    safe = klass.replace("\\", "\\\\").replace("'", "\\'")
    return f"(class_g ?= '{safe}' || class_i ?= '{safe}')"


def _opacity_block(settings):
    if not settings["opacity_enabled"] and not settings["opacity_exclude"] and int(settings["opacity"]) == 80:
        return ""
    amount = min(100, max(15, int(settings["opacity"])))
    enabled = "true" if settings["opacity_enabled"] else "false"
    lines = ["# picom-panel-opacity", f"# enabled = {enabled};", f"# amount = {amount};"]
    for klass in settings["opacity_exclude"]:
        lines.append(f"# exclude = {klass};")
    if settings["opacity_enabled"]:
        excluded = " && ".join(f"!{_class_match(klass)}" for klass in settings["opacity_exclude"])
        general = "window_type != 'desktop'"
        if excluded:
            general = f"{general} && {excluded}"
        lines.extend([
            "  {",
            f'    match = "{general}";',
            f"    opacity = {amount / 100:.2f};",
            "  },",
        ])
        for klass in settings["opacity_exclude"]:
            lines.extend([
                "  {",
                f'    match = "{_class_match(klass)}";',
                "    opacity = 1.0;",
                "  },",
            ])
    lines.append("# /picom-panel-opacity")
    return "\n".join(lines) + "\n"


def picom_config_text(text, settings):
    radius = min(99, max(0, int(settings["corner_radius"])))
    fade = min(100, max(0, int(settings["fading"])))
    color = settings["shadow_color"]
    if not color.startswith("#"):
        color = "#" + color
    backend = settings.get("backend", "glx")
    if backend not in ("glx", "egl", "xrender"):
        backend = "glx"
    text = _set_picom_scalar(text, "backend", f'"{backend}"')
    text = _set_picom_scalar(text, "vsync", "true" if settings.get("vsync", True) else "false")
    text = _set_picom_scalar(text, "corner-radius", str(radius))
    text = _set_picom_scalar(text, "shadow", "true" if settings["shadow"] else "false")
    text = _set_picom_scalar(text, "shadow-color", f'"{color}"')
    text = _set_picom_scalar(text, "fading", "true" if fade else "false")
    if fade:
        step = f"{fade / 100:.2f}"
        text = _set_picom_scalar(text, "fade-in-step", step)
        text = _set_picom_scalar(text, "fade-out-step", step)
    text = _set_picom_scalar(text, "blur-background", "true" if settings["blur"] else "false")
    catchall = re.compile(r"\n[ \t]*\{\s*blur-background\s*=\s*false\s*;\s*\},?")
    if settings["blur"]:
        text = catchall.sub("", text, count=1)
    elif not re.search(r"\{\s*blur-background\s*=\s*false\s*;", text):
        text = text.replace("rules: (", "rules: (\n  { blur-background = false; },", 1)
    text = re.sub(r"\n?# picom-panel-animations\n.*?# /picom-panel-animations\n?", "\n", text, flags=re.S)
    if settings["animations"]:
        if not text.endswith("\n"):
            text += "\n"
        text += _PICOM_ANIMATIONS
    text = text.replace(
        'match = "class_g = \'Polybar\'";',
        f'match = "{_SQUARE_MATCH}";',
        1,
    )
    text = text.replace(
        'match = "class_g = \'Polybar\' || class_g = \'Dunst\'";',
        f'match = "{_SQUARE_MATCH}";',
        1,
    )
    if "class_g = 'Dunst'" not in text:
        text = text.replace("rules: (", "rules: (\n" + _SQUARE_RULE, 1)
    text = _OPACITY_BLOCK.sub("\n", text)
    block = _opacity_block(settings)
    if block:
        text = text.replace("rules: (", "rules: (\n" + block, 1)
    text = re.sub(r"(rules: \()\n(?:[ \t]*\n)+", r"\1\n", text, count=1)
    text = re.sub(r"(# /picom-panel-opacity)\n(?:[ \t]*\n)+", r"\1\n", text, count=1)
    return text


def picom_config_works(text):
    fd, name = tempfile.mkstemp(suffix=".conf")
    os.close(fd)
    path = Path(name)
    path.write_text(text)
    proc = subprocess.Popen(
        ["picom", "--config", str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        _, err = proc.communicate(timeout=1)
    except subprocess.TimeoutExpired:
        err = b""
        proc.kill()
        proc.wait(timeout=1)
    path.unlink(missing_ok=True)
    message = err.decode(errors="replace")
    return "Failed to get configuration" not in message and "error when parsing" not in message


def reload_picom():
    subprocess.run(["pkill", "-x", "picom"], check=False)
    for _ in range(40):
        if subprocess.call(["pgrep", "-x", "picom"], stdout=subprocess.DEVNULL) != 0:
            break
        time.sleep(0.05)
    subprocess.Popen(
        ["picom", "--config", str(PICOM_CONF)],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def current_picom_settings():
    if _picom["values"] is None:
        _picom["values"] = read_picom_settings()
    return _picom["values"]


def apply_picom_settings():
    if _picom["values"] is None or not PICOM_CONF.is_file():
        return
    original = PICOM_CONF.read_text()
    updated = picom_config_text(original, _picom["values"])
    if updated == original or not picom_config_works(updated):
        return
    PICOM_CONF.write_text(updated)
    reload_picom()


DUNST_CONF = Path.home() / ".config/dunst/dunstrc"
_DUNST_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
_DUNST_ORIGINS = [
    "top-left",
    "top-center",
    "top-right",
    "left-center",
    "right-center",
    "bottom-left",
    "bottom-center",
    "bottom-right",
]
_DUNST_CORNERS = [
    "all",
    "top",
    "bottom",
    "left",
    "right",
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
]
DUNST_FIELDS = [
    ("choice", "origin", "Position:", _DUNST_ORIGINS),
    ("int", "offset_x", "Offset X:", -400, 400),
    ("int", "offset_y", "Offset Y:", -400, 400),
    ("int", "width", "Width:", 50, 800),
    ("int", "height_min", "Min height:", 0, 400),
    ("int", "height_max", "Max height:", 0, 600),
    ("int", "corner_radius", "Radius:", 0, 48),
    ("choice", "corners", "Corners:", _DUNST_CORNERS),
    ("int", "icon_corner_radius", "Icon radius:", 0, 48),
    ("int", "progress_bar_corner_radius", "Progress radius:", 0, 24),
    ("int", "padding", "Vertical padding:", 0, 64),
    ("int", "horizontal_padding", "Horizontal padding:", 0, 64),
    ("int", "text_icon_padding", "Icon padding:", 0, 64),
    ("int", "gap_size", "Gap:", 0, 40),
    ("choice", "alignment", "Alignment:", ["left", "center", "right"]),
    ("choice", "vertical_alignment", "Vertical alignment:", ["top", "center", "bottom"]),
    ("choice", "icon_position", "Icon:", ["off", "left", "right", "top"]),
    ("int", "min_icon_size", "Min icon:", 0, 256),
    ("int", "max_icon_size", "Max icon:", 0, 256),
    ("int", "transparency", "Transparency:", 0, 100),
    ("int", "separator_height", "Separator:", 0, 16),
    ("int", "line_height", "Line height:", 0, 48),
    ("int", "notification_limit", "Limit:", 0, 20),
]
DUNST_TIMEOUTS = [
    ("urgency_low", "Low timeout:"),
    ("urgency_normal", "Normal timeout:"),
    ("urgency_critical", "Critical timeout:"),
]
_DUNST_INT_DEFAULTS = {
    "offset_x": 0,
    "offset_y": 0,
    "width": 300,
    "height_min": 0,
    "height_max": 300,
    "corner_radius": 0,
    "icon_corner_radius": 0,
    "progress_bar_corner_radius": 0,
    "padding": 0,
    "horizontal_padding": 0,
    "text_icon_padding": 0,
    "min_icon_size": 0,
    "max_icon_size": 0,
    "gap_size": 0,
    "transparency": 0,
    "separator_height": 0,
    "line_height": 0,
    "notification_limit": 0,
}
_DUNST_STR_DEFAULTS = {
    "origin": "top-center",
    "corners": "all",
    "alignment": "center",
    "vertical_alignment": "center",
    "icon_position": "left",
}
_DUNST_PAIR_KEYS = {"offset_x", "offset_y", "height_min", "height_max"}
_dunst = {"values": None, "fonts": None}


def parse_dunst_pair(value, fallback):
    raw = value.strip().strip("()")
    if "," in raw:
        left, right = raw.split(",", 1)
    elif raw.lstrip("-").isdigit():
        number = int(raw)
        return number, number
    else:
        return fallback
    try:
        return int(left.strip()), int(right.strip())
    except ValueError:
        return fallback


def split_font(spec):
    parts = spec.rsplit(None, 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0], parts[1]
    return spec, "11"


def dunst_color_label(section, key):
    key_name = {
        "background": "background",
        "foreground": "foreground",
        "frame_color": "frame",
    }.get(key, key.replace("_", " "))
    prefix = {
        "urgency_low": "Low",
        "urgency_normal": "Normal",
        "urgency_critical": "Critical",
        "global": "Global",
    }.get(section, section.replace("_", " ").title())
    return f"{prefix} {key_name}:"


def system_fonts():
    if _dunst["fonts"] is None:
        try:
            out = subprocess.check_output(["fc-list", "-f", "%{family[0]}\n"], text=True)
            _dunst["fonts"] = sorted(
                {line.strip() for line in out.splitlines() if line.strip()},
                key=str.casefold,
            )
        except (OSError, subprocess.CalledProcessError):
            _dunst["fonts"] = []
    return _dunst["fonts"]


def read_dunst_settings():
    text = DUNST_CONF.read_text() if DUNST_CONF.is_file() else ""
    section = None
    family, size = "Liberation Sans", "11"
    frame_width = 0
    ints = dict(_DUNST_INT_DEFAULTS)
    strs = dict(_DUNST_STR_DEFAULTS)
    colors = {}
    order = []
    timeouts = {section: 10 for section, _label in DUNST_TIMEOUTS}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1].strip()
            continue
        if section is None or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if section == "global" and key == "font":
            family, size = split_font(value)
        if section == "global" and key == "frame_width":
            frame_width = int(value) if value.isdigit() else 0
        if section == "global" and key in _DUNST_INT_DEFAULTS and value.lstrip("-").isdigit():
            ints[key] = int(value)
        if section == "global" and key in _DUNST_STR_DEFAULTS:
            strs[key] = value
        if section == "global" and key == "offset":
            ints["offset_x"], ints["offset_y"] = parse_dunst_pair(value, (0, 0))
        if section == "global" and key == "height":
            ints["height_min"], ints["height_max"] = parse_dunst_pair(value, (0, 300))
        if section in timeouts and key == "timeout" and value.isdigit():
            timeouts[section] = int(value)
        if _DUNST_COLOR.fullmatch(value):
            pair = (section, key)
            if pair not in colors:
                order.append(pair)
            colors[pair] = value
    return {
        "family": family,
        "size": size,
        "frame_width": frame_width,
        "frame_width_on": frame_width or 2,
        "ints": ints,
        "strs": strs,
        "colors": colors,
        "order": order,
        "timeouts": timeouts,
    }


def replace_dunst_key(text, section, key, rendered):
    lines = text.splitlines(keepends=True)
    current = None
    target = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            current = stripped[1:-1].strip()
            continue
        if current != section or "=" not in stripped:
            continue
        if stripped.split("=", 1)[0].strip() == key:
            target = index
    if target is None:
        return text
    raw = lines[target]
    indent = raw[: len(raw) - len(raw.lstrip(" \t"))]
    ending = "\n" if raw.endswith("\n") else ""
    lines[target] = f"{indent}{key} = {rendered}{ending}"
    return "".join(lines)


def dunst_config_text(text, settings):
    font = f"{settings['family']} {settings['size']}".strip()
    text = replace_dunst_key(text, "global", "font", font)
    text = replace_dunst_key(text, "global", "frame_width", str(int(settings["frame_width"])))
    for key, value in settings["ints"].items():
        if key in _DUNST_PAIR_KEYS:
            continue
        text = replace_dunst_key(text, "global", key, str(int(value)))
    for key, value in settings["strs"].items():
        text = replace_dunst_key(text, "global", key, value)
    text = replace_dunst_key(
        text,
        "global",
        "offset",
        f"({int(settings['ints']['offset_x'])}, {int(settings['ints']['offset_y'])})",
    )
    text = replace_dunst_key(
        text,
        "global",
        "height",
        f"({int(settings['ints']['height_min'])}, {int(settings['ints']['height_max'])})",
    )
    for section, key in settings["order"]:
        text = replace_dunst_key(text, section, key, f'"{settings["colors"][(section, key)]}"')
    for section, _label in DUNST_TIMEOUTS:
        text = replace_dunst_key(text, section, "timeout", str(int(settings["timeouts"][section])))
    return text


def reload_dunst():
    result = subprocess.run(
        ["dunstctl", "reload"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        return
    subprocess.run(["pkill", "-x", "dunst"], check=False)
    subprocess.Popen(
        ["dunst"],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def current_dunst_settings():
    if _dunst["values"] is None:
        _dunst["values"] = read_dunst_settings()
    return _dunst["values"]


def apply_dunst_settings():
    if _dunst["values"] is None or not DUNST_CONF.is_file():
        return
    original = DUNST_CONF.read_text()
    updated = dunst_config_text(original, _dunst["values"])
    if updated == original:
        return
    DUNST_CONF.write_text(updated)
    reload_dunst()


KITTY_CONF = Path.home() / ".config/kitty/kitty.conf"
_kitty = {"values": None}
KITTY_LABELS = {
    "confirm_os_window_close": "Confirm close:",
    "enable_audio_bell": "Audio bell:",
    "visual_bell_duration": "Visual bell:",
    "window_alert_on_bell": "Window alert:",
    "background": "Background:",
    "foreground": "Foreground:",
    "active_border_color": "Active border:",
    "inactive_border_color": "Inactive border:",
    "font_size": "Font size:",
}


def _kitty_entries(text):
    entries = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split(None, 1)
        key = parts[0]
        value = parts[1] if len(parts) > 1 else ""
        entries.append((key, value))
    return entries


def read_kitty_settings():
    text = KITTY_CONF.read_text() if KITTY_CONF.is_file() else ""
    values = {}
    order = []
    for key, value in _kitty_entries(text):
        if key not in KITTY_LABELS:
            continue
        if key not in order:
            order.append(key)
        values[key] = value
    if "font_size" not in values:
        order.append("font_size")
        values["font_size"] = "11"
    foreground = values.get("foreground", "#DBD6DD")
    for key in ("active_border_color", "inactive_border_color"):
        if key not in values:
            order.append(key)
            values[key] = foreground
    return {"order": order, "values": values}


def kitty_yes(value):
    return value.strip().lower() in ("yes", "y", "true", "on", "1")


def kitty_confirm(value):
    token = value.split(None, 1)[0] if value.strip() else "0"
    try:
        return int(token) != 0
    except ValueError:
        return False


def kitty_seconds(value):
    token = value.split(None, 1)[0] if value.strip() else "0"
    try:
        return float(token)
    except ValueError:
        return 0.0


def kitty_seconds_text(value, seconds):
    rest = value.split()[1:]
    if abs(seconds - round(seconds)) < 0.05:
        rendered = str(int(round(seconds)))
    else:
        rendered = f"{seconds:.1f}"
    if rest:
        return rendered + " " + " ".join(rest)
    return rendered


def replace_kitty_key(text, key, value):
    lines = text.splitlines(keepends=True)
    target = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.split(None, 1)[0] == key:
            target = index
    if target is None:
        if text and not text.endswith("\n"):
            text += "\n"
        return text + f"{key} {value}\n"
    raw = lines[target]
    indent = raw[: len(raw) - len(raw.lstrip(" \t"))]
    ending = "\n" if raw.endswith("\n") else ""
    lines[target] = f"{indent}{key} {value}{ending}"
    return "".join(lines)


def kitty_config_text(text, settings):
    for key in settings["order"]:
        text = replace_kitty_key(text, key, settings["values"][key])
    return text


def reload_kitty():
    subprocess.run(["pkill", "-USR1", "-x", "kitty"], check=False)


def current_kitty_settings():
    if _kitty["values"] is None:
        _kitty["values"] = read_kitty_settings()
    return _kitty["values"]


def apply_kitty_settings():
    if _kitty["values"] is None or not KITTY_CONF.is_file():
        return
    original = KITTY_CONF.read_text()
    updated = kitty_config_text(original, _kitty["values"])
    if updated == original:
        return
    KITTY_CONF.write_text(updated)
    reload_kitty()


_launchers = None
_autostart = {"entries": None}


def autostart_path():
    return Path.home() / ".config" / "bspwm" / "rices" / get_current_theme() / "config" / "autostart"


def desktop_apps():
    global _launchers
    if _launchers is not None:
        return _launchers
    apps = []
    seen = set()
    data_home = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))
    data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":")
    for base in [data_home, *data_dirs]:
        directory = Path(base) / "applications"
        if not directory.is_dir():
            continue
        for path in directory.glob("*.desktop"):
            name = wm_class = exec_name = None
            hidden = False
            for line in path.read_text(errors="replace").splitlines():
                if line.startswith("["):
                    if line.strip() != "[Desktop Entry]":
                        break
                    continue
                if line.startswith("Name=") and name is None:
                    name = line.split("=", 1)[1].strip()
                elif line.startswith("StartupWMClass="):
                    wm_class = line.split("=", 1)[1].strip()
                elif line.startswith("Exec=") and exec_name is None:
                    raw = line.split("=", 1)[1].strip().strip('"')
                    parts = [part.strip('"') for part in raw.split() if part and not part.startswith("%")]
                    if parts:
                        exec_name = Path(parts[0]).name
                elif line in ("NoDisplay=true", "Hidden=true"):
                    hidden = True
            if hidden or not name or not exec_name:
                continue
            klass = wm_class or (name if " " not in name else exec_name)
            if klass in seen:
                continue
            seen.add(klass)
            apps.append({"name": name, "class": klass, "exec": exec_name})
    _launchers = sorted(apps, key=lambda app: app["name"].casefold())
    return _launchers


def launcher_for(class_name, instance):
    for app in desktop_apps():
        if app["class"] == class_name:
            return app
    for app in desktop_apps():
        if app["exec"] in (instance, class_name):
            return app
    return None


def _autostart_number(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _autostart_field(value):
    text = "" if value is None else str(value)
    return text if text else "-"


def _autostart_text(value):
    return "" if value == "-" else value


def read_autostart():
    path = autostart_path()
    entries = []
    if not path.is_file():
        return entries
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        parts += [""] * (12 - len(parts))
        entries.append({
            "class": _autostart_text(parts[0]),
            "exec": _autostart_text(parts[1]),
            "url": _autostart_text(parts[2]),
            "desktop": max(1, _autostart_number(parts[3], 1)),
            "floating": parts[4] == "1",
            "x": _autostart_number(parts[5]),
            "y": _autostart_number(parts[6]),
            "w": _autostart_number(parts[7]),
            "h": _autostart_number(parts[8]),
            "sw": _autostart_number(parts[9]),
            "sh": _autostart_number(parts[10]),
            "title": _autostart_text(parts[11]).replace("\t", " "),
        })
    return entries


def current_autostart():
    if _autostart["entries"] is None:
        _autostart["entries"] = read_autostart()
    return _autostart["entries"]


def save_autostart():
    if _autostart["entries"] is None:
        return
    path = autostart_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# class\texec\turl\tdesktop\tfloating\tx\ty\tw\th\tsw\tsh\ttitle"]
    for entry in _autostart["entries"]:
        lines.append("\t".join([
            _autostart_field(entry["class"]),
            _autostart_field(entry["exec"]),
            _autostart_field(entry["url"]),
            str(int(entry["desktop"])),
            "1" if entry["floating"] else "0",
            str(int(entry["x"])),
            str(int(entry["y"])),
            str(int(entry["w"])),
            str(int(entry["h"])),
            str(int(entry.get("sw") or 0)),
            str(int(entry.get("sh") or 0)),
            _autostart_field((entry.get("title") or "").replace("\t", " ")),
        ]))
    path.write_text("\n".join(lines) + "\n")


def desktop_count():
    try:
        names = subprocess.check_output(["bspc", "query", "-D", "--names"], text=True).split()
    except (OSError, subprocess.CalledProcessError):
        return 1
    return max(1, len(names))


def open_windows():
    try:
        ids = subprocess.check_output(["bspc", "query", "-N", "-n", ".window"], text=True).split()
        desks = subprocess.check_output(["bspc", "query", "-D"], text=True).split()
    except (OSError, subprocess.CalledProcessError):
        return []
    windows = []
    monitors = {}
    for node_id in ids:
        try:
            node = json.loads(subprocess.check_output(["bspc", "query", "-T", "-n", node_id], text=True))
            desk_id = subprocess.check_output(["bspc", "query", "-D", "-n", node_id], text=True).strip()
            mon_id = subprocess.check_output(["bspc", "query", "-M", "-n", node_id], text=True).strip()
            if mon_id not in monitors:
                mon = json.loads(subprocess.check_output(["bspc", "query", "-T", "-m", mon_id], text=True))
                monitors[mon_id] = mon.get("rectangle") or {}
        except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
            continue
        client = node.get("client") or {}
        if not client.get("className"):
            continue
        rect = node.get("rectangle") or {}
        screen = monitors.get(mon_id) or {}
        try:
            title = subprocess.check_output(
                ["xdotool", "getwindowname", node_id], text=True, stderr=subprocess.DEVNULL
            ).strip().replace("\t", " ")
        except (OSError, subprocess.CalledProcessError):
            title = ""
        windows.append({
            "class": client["className"],
            "instance": client.get("instanceName") or "",
            "title": title,
            "floating": client.get("state") == "floating",
            "desktop": desks.index(desk_id) + 1 if desk_id in desks else 1,
            "x": int(rect.get("x", 0)) - int(screen.get("x", 0)),
            "y": int(rect.get("y", 0)) - int(screen.get("y", 0)),
            "w": int(rect.get("width", 0)),
            "h": int(rect.get("height", 0)),
            "sw": int(screen.get("width", 0)),
            "sh": int(screen.get("height", 0)),
        })
    return windows


def _firefox_roots():
    roots = []
    for base in (Path.home() / ".mozilla" / "firefox", Path.home() / ".config" / "mozilla" / "firefox"):
        if (base / "profiles.ini").is_file():
            roots.append(base)
    return roots


def _firefox_recovery_files():
    files = []
    for root in _firefox_roots():
        section = {}
        sections = []
        for line in (root / "profiles.ini").read_text(errors="replace").splitlines():
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                if section:
                    sections.append(section)
                section = {}
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                section[key] = value
        if section:
            sections.append(section)
        sections.sort(key=lambda item: item.get("Default") != "1")
        for item in sections:
            raw = item.get("Path")
            if not raw:
                continue
            profile = Path(raw) if item.get("IsRelative") == "0" else root / raw
            for name in ("sessionstore-backups/recovery.jsonlz4", "sessionstore.jsonlz4"):
                path = profile / name
                if path.is_file():
                    files.append(path)
    return files


def _read_mozlz4(path):
    try:
        data = Path(path).read_bytes()
    except OSError:
        return None
    if not data.startswith(b"mozLz40\x00"):
        return None
    payload = data[8:]
    if len(payload) < 4:
        return None
    size = int.from_bytes(payload[:4], "little")
    if size <= 0 or size > 64_000_000:
        return None
    try:
        lib = ctypes.CDLL("liblz4.so.1")
    except OSError:
        return None
    lib.LZ4_decompress_safe.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
    lib.LZ4_decompress_safe.restype = ctypes.c_int
    dest = ctypes.create_string_buffer(size)
    read = lib.LZ4_decompress_safe(payload[4:], dest, len(payload) - 4, size)
    if read < 1:
        return None
    try:
        return json.loads(dest.raw[:read])
    except json.JSONDecodeError:
        return None


def _session_pages(session):
    pages = []

    def take(windows):
        history = []
        for win in windows or []:
            if not isinstance(win, dict):
                continue
            for tab in win.get("tabs") or []:
                entries = tab.get("entries") or []
                index = tab.get("index") or 0
                for number, entry in enumerate(entries, start=1):
                    url = entry.get("url") or ""
                    title = entry.get("title") or ""
                    if not title or not url.startswith(("http://", "https://")):
                        continue
                    item = (title, url)
                    if number == index:
                        pages.append(item)
                    else:
                        history.append(item)
        pages.extend(history)

    take(session.get("windows"))
    last = session.get("lastSessionState") or {}
    if isinstance(last, dict):
        take(last.get("windows"))
    take(session.get("_closedWindows"))
    if isinstance(last, dict):
        take(last.get("_closedWindows"))
    return pages


def firefox_url(title):
    page = title or ""
    for suffix in (
        " — Mozilla Firefox (Private Browsing)",
        " — Mozilla Firefox",
        " - Mozilla Firefox (Private Browsing)",
        " - Mozilla Firefox",
    ):
        if page.endswith(suffix):
            page = page[: -len(suffix)]
            break
    page = page.strip()
    if not page:
        return ""
    for path in _firefox_recovery_files():
        session = _read_mozlz4(path)
        if not session:
            continue
        for tab_title, url in _session_pages(session):
            if tab_title == page:
                return url
    return ""


def entry_from_window(window):
    app = launcher_for(window["class"], window["instance"])
    exec_name = app["exec"] if app else window["instance"]
    url = firefox_url(window.get("title") or "") if exec_name == "firefox" or window["class"] == "firefox" else ""
    return {
        "class": window["class"],
        "exec": exec_name,
        "url": url,
        "title": window.get("title") or "",
        "desktop": window["desktop"],
        "floating": window["floating"],
        "x": window["x"],
        "y": window["y"],
        "w": window["w"],
        "h": window["h"],
        "sw": window.get("sw", 0),
        "sh": window.get("sh", 0),
    }


def run_autostart():
    script = Path.home() / ".config" / "bspwm" / "bin" / "autostart.sh"
    if script.is_file():
        subprocess.Popen([str(script)], start_new_session=True)