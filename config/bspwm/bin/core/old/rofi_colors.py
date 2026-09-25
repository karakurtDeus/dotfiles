import re
from pathlib import Path


ROFI_DIR = Path.home() / ".config" / "bspwm" / "rofi"
THEMES = ("drun.rasi", "select.rasi")

COLOR_LINE = re.compile(
    r"^(\s*)([A-Za-z0-9_-]+)(\s*:\s*)(#[0-9A-Fa-f]{3,8})(\s*;\s*)$"
)


def load_rofi_colors(directory=ROFI_DIR):
    colors = []
    seen = set()
    for theme in THEMES:
        path = directory / theme
        if not path.is_file():
            continue
        for line in path.read_text().splitlines():
            match = COLOR_LINE.match(line)
            if not match or match.group(2) in seen:
                continue
            seen.add(match.group(2))
            colors.append((match.group(2), match.group(4)))
    return colors


def save_rofi_colors(colors, directory=ROFI_DIR):
    updates = dict(colors)
    for theme in THEMES:
        path = directory / theme
        if not path.is_file():
            continue
        new_lines = []
        for line in path.read_text().splitlines():
            match = COLOR_LINE.match(line)
            if match and match.group(2) in updates:
                name = match.group(2)
                line = (
                    f"{match.group(1)}{name}{match.group(3)}"
                    f"{updates[name]}{match.group(5)}"
                )
            new_lines.append(line)
        path.write_text("\n".join(new_lines) + "\n")
