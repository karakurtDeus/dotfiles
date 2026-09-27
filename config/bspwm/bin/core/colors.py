from pathlib import Path
import re

from imgui_bundle import ImVec4

COLORS_FILE = Path.home() / ".config" / "polybar" / "colors.ini"

_DEFAULTS = {
    "control_panel_bg": "#161117",
    "control_panel_accent": "#D9ADE8",
    "control_panel_text": "#DBD6DD",
    "control_panel_button_text": "#DBD6DD",
    "control_panel_button": "#1B191C",
    "control_panel_button_hovered": "#4B3E50",
    "control_panel_button_active": "#4B3E50",
    "control_panel_frame": "#1B191C",
    "control_panel_frame_hovered": "#1B191C",
    "control_panel_frame_active": "#1B191C",
    "control_panel_tab": "#1B191C",
    "control_panel_tab_hovered": "#4A3D50",
    "control_panel_tab_selected": "#4A3D50",
    "control_panel_popup": "#1B191C",
    "control_panel_popup_border": "#4A3D50",
    "control_panel_header": "#4A3D50",
    "control_panel_header_hovered": "#4A3D50",
    "control_panel_header_active": "#4A3D50",
}


def hex_to_color(hex_color):
    value = hex_color.lstrip("#")
    r = int(value[0:2], 16) / 255
    g = int(value[2:4], 16) / 255
    b = int(value[4:6], 16) / 255
    return ImVec4(r, g, b, 1.0)


def color_to_hex(color):
    r = int(color.x * 255)
    g = int(color.y * 255)
    b = int(color.z * 255)
    return f"#{r:02X}{g:02X}{b:02X}"


def _load_colors():
    found = {}
    if not COLORS_FILE.is_file():
        return found
    for line in COLORS_FILE.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key.startswith("control_panel_") and value:
            found[key] = value if value.startswith("#") else f"#{value}"
    return found


_colors = _load_colors()


def _color(key):
    return hex_to_color(_colors.get(key) or _DEFAULTS[key])


GUI_BG = _color("control_panel_bg")
GUI_ACCENT = _color("control_panel_accent")
GUI_TEXT = _color("control_panel_text")
GUI_BUTTON_TEXT = _color("control_panel_button_text")
GUI_BUTTON = _color("control_panel_button")
GUI_BUTTON_HOVERED = _color("control_panel_button_hovered")
GUI_BUTTON_ACTIVE = _color("control_panel_button_active")
GUI_FRAME = _color("control_panel_frame")
GUI_FRAME_HOVERED = _color("control_panel_frame_hovered")
GUI_FRAME_ACTIVE = _color("control_panel_frame_active")
GUI_TAB = _color("control_panel_tab")
GUI_TAB_HOVERED = _color("control_panel_tab_hovered")
GUI_TAB_SELECTED = _color("control_panel_tab_selected")
GUI_POPUP = _color("control_panel_popup")
GUI_POPUP_BORDER = _color("control_panel_popup_border")
GUI_HEADER = _color("control_panel_header")
GUI_HEADER_HOVERED = _color("control_panel_header_hovered")
GUI_HEADER_ACTIVE = _color("control_panel_header_active")

LOCKSCREEN_FIELDS = (
    ("lockscreen_bg", "Background:"),
    ("lockscreen_fg", "Foreground:"),
    ("lockscreen_ring", "Ring:"),
    ("lockscreen_date", "Date:"),
    ("lockscreen_verify", "Verify:"),
    ("lockscreen_wrong", "Wrong:"),
)
PANEL_FIELDS = (
    ("control_panel_bg", "Background:"),
    ("control_panel_accent", "Accent:"),
    ("control_panel_text", "Text:"),
    ("control_panel_button_text", "Button text:"),
    ("control_panel_button", "Button:"),
    ("control_panel_button_hovered", "Button hovered:"),
    ("control_panel_button_active", "Button active:"),
    ("control_panel_frame", "Frame:"),
    ("control_panel_frame_hovered", "Frame hovered:"),
    ("control_panel_frame_active", "Frame active:"),
    ("control_panel_tab", "Tab:"),
    ("control_panel_tab_hovered", "Tab hovered:"),
    ("control_panel_tab_selected", "Tab selected:"),
    ("control_panel_popup", "Popup:"),
    ("control_panel_popup_border", "Popup border:"),
    ("control_panel_header", "Header:"),
    ("control_panel_header_hovered", "Header hovered:"),
    ("control_panel_header_active", "Header active:"),
)
_GUI = {
    "control_panel_bg": GUI_BG,
    "control_panel_accent": GUI_ACCENT,
    "control_panel_text": GUI_TEXT,
    "control_panel_button_text": GUI_BUTTON_TEXT,
    "control_panel_button": GUI_BUTTON,
    "control_panel_button_hovered": GUI_BUTTON_HOVERED,
    "control_panel_button_active": GUI_BUTTON_ACTIVE,
    "control_panel_frame": GUI_FRAME,
    "control_panel_frame_hovered": GUI_FRAME_HOVERED,
    "control_panel_frame_active": GUI_FRAME_ACTIVE,
    "control_panel_tab": GUI_TAB,
    "control_panel_tab_hovered": GUI_TAB_HOVERED,
    "control_panel_tab_selected": GUI_TAB_SELECTED,
    "control_panel_popup": GUI_POPUP,
    "control_panel_popup_border": GUI_POPUP_BORDER,
    "control_panel_header": GUI_HEADER,
    "control_panel_header_hovered": GUI_HEADER_HOVERED,
    "control_panel_header_active": GUI_HEADER_ACTIVE,
}
_theme = {"values": None}
_HEX = re.compile(r"#[0-9A-Fa-f]{6}")


def read_theme_colors():
    values = {}
    if not COLORS_FILE.is_file():
        return values
    for line in COLORS_FILE.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not (key.startswith("lockscreen_") or key.startswith("control_panel_")):
            continue
        if value and not value.startswith("#"):
            value = "#" + value
        values[key] = value
    return values


def current_theme_colors():
    if _theme["values"] is None:
        _theme["values"] = read_theme_colors()
    return _theme["values"]


def _replace_theme_color(text, key, hex_color):
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        if stripped.split("=", 1)[0].strip() != key:
            continue

        def repl(match, new=hex_color):
            old = match.group(0)
            return old if old.lower() == new.lower() else new

        lines[index] = _HEX.sub(repl, line, count=1)
        break
    return "".join(lines)


def paint_panel_colors(values):
    for key, vec in _GUI.items():
        hex_color = values.get(key)
        if not hex_color:
            continue
        color = hex_to_color(hex_color)
        vec.x = color.x
        vec.y = color.y
        vec.z = color.z
        vec.w = color.w


def apply_theme_colors():
    if _theme["values"] is None or not COLORS_FILE.is_file():
        return
    original = COLORS_FILE.read_text()
    updated = original
    for key, value in _theme["values"].items():
        if key.startswith("lockscreen_") or key.startswith("control_panel_"):
            updated = _replace_theme_color(updated, key, value)
    if updated != original:
        COLORS_FILE.write_text(updated)
    paint_panel_colors(_theme["values"])


ROFI_FILES = ("powermenu", "select", "drun")
ROFI_LABELS = {
    "bg": "Background:",
    "fg": "Foreground:",
    "primary": "Primary:",
    "disabled": "Disabled:",
}
_ROFI_LINE = re.compile(r"^(\s*)(bg|fg|primary|disabled)(\s*:\s*)(#[0-9A-Fa-f]{6})(\s*;.*)$")
_rofi = {"values": None}


def rofi_theme_path(name, theme):
    return Path.home() / ".config" / "bspwm" / "rices" / theme / "rofi" / f"{name}.rasi"


def read_rofi_colors():
    from control_panel import get_current_theme

    theme = get_current_theme()
    files = {}
    for name in ROFI_FILES:
        path = rofi_theme_path(name, theme)
        colors = {}
        if path.is_file():
            for line in path.read_text().splitlines():
                match = _ROFI_LINE.match(line)
                if match:
                    colors[match.group(2)] = match.group(4)
        files[name] = colors
    return {"theme": theme, "files": files}


def current_rofi_colors():
    if _rofi["values"] is None:
        _rofi["values"] = read_rofi_colors()
    return _rofi["values"]


def _replace_rofi_color(text, key, hex_color):
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        body = line[:-1] if line.endswith("\n") else line
        match = _ROFI_LINE.match(body)
        if not match or match.group(2) != key:
            continue
        old = match.group(4)
        new = old if old.lower() == hex_color.lower() else hex_color
        ending = "\n" if line.endswith("\n") else ""
        lines[index] = f"{match.group(1)}{match.group(2)}{match.group(3)}{new}{match.group(5)}{ending}"
        break
    return "".join(lines)


BTOP_THEME = Path.home() / ".config" / "btop" / "themes" / "colors.theme"
BTOP_GROUPS = (
    ("Colors", (
        ("main_bg", "Background:"),
        ("main_fg", "Foreground:"),
        ("title", "Title:"),
        ("hi_fg", "Highlight:"),
        ("selected_bg", "Selected:"),
        ("selected_fg", "Selected text:"),
        ("inactive_fg", "Inactive:"),
        ("graph_text", "Graph text:"),
        ("meter_bg", "Meter:"),
        ("proc_misc", "Process misc:"),
        ("div_line", "Divider:"),
    )),
    ("Boxes", (
        ("cpu_box", "CPU:"),
        ("mem_box", "Memory:"),
        ("net_box", "Network:"),
        ("proc_box", "Processes:"),
    )),
    ("CPU", (("cpu_start", "Low:"), ("cpu_mid", "Mid:"), ("cpu_end", "High:"))),
    ("Temperature", (("temp_start", "Low:"), ("temp_mid", "Mid:"), ("temp_end", "High:"))),
    ("Used", (("used_start", "Low:"), ("used_mid", "Mid:"), ("used_end", "High:"))),
    ("Free", (("free_start", "Low:"), ("free_mid", "Mid:"), ("free_end", "High:"))),
    ("Cached", (("cached_start", "Low:"), ("cached_mid", "Mid:"), ("cached_end", "High:"))),
    ("Available", (("available_start", "Low:"), ("available_mid", "Mid:"), ("available_end", "High:"))),
    ("Download", (("download_start", "Low:"), ("download_mid", "Mid:"), ("download_end", "High:"))),
    ("Upload", (("upload_start", "Low:"), ("upload_mid", "Mid:"), ("upload_end", "High:"))),
    ("Processes", (("process_start", "Low:"), ("process_mid", "Mid:"), ("process_end", "High:"))),
)
_BTOP_LINE = re.compile(r'^(theme\[)([A-Za-z0-9_]+)(\]=")(#[0-9A-Fa-f]{6})(".*)$')
_btop = {"values": None}


def read_btop_colors():
    colors = {}
    if BTOP_THEME.is_file():
        for line in BTOP_THEME.read_text().splitlines():
            match = _BTOP_LINE.match(line.strip())
            if match:
                colors[match.group(2)] = match.group(4)
    return colors


def current_btop_colors():
    if _btop["values"] is None:
        _btop["values"] = read_btop_colors()
    return _btop["values"]


def _replace_btop_color(text, key, hex_color):
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        body = line[:-1] if line.endswith("\n") else line
        match = _BTOP_LINE.match(body)
        if not match or match.group(2) != key:
            continue
        old = match.group(4)
        new = old if old.lower() == hex_color.lower() else hex_color
        ending = "\n" if line.endswith("\n") else ""
        lines[index] = f"{match.group(1)}{match.group(2)}{match.group(3)}{new}{match.group(5)}{ending}"
        break
    return "".join(lines)


def apply_btop_colors():
    if _btop["values"] is None or not BTOP_THEME.is_file():
        return
    original = BTOP_THEME.read_text()
    updated = original
    for key, value in _btop["values"].items():
        updated = _replace_btop_color(updated, key, value)
    if updated != original:
        BTOP_THEME.write_text(updated)


def apply_rofi_colors():
    if _rofi["values"] is None:
        return
    theme = _rofi["values"]["theme"]
    for name, colors in _rofi["values"]["files"].items():
        path = rofi_theme_path(name, theme)
        if not path.is_file():
            continue
        original = path.read_text()
        updated = original
        for key, value in colors.items():
            updated = _replace_rofi_color(updated, key, value)
        if updated != original:
            path.write_text(updated)
