import getpass

def return_username():
    return getpass.getuser()

from pathlib import Path
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
    "(class_g = 'Rofi' && (name = 'rofi - wallpaper' || name = 'rofi - powermenu'))"
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