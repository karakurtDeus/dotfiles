from pathlib import Path


LOCKSCREEN = Path.home() / ".config" / "bspwm" / "bin" / "lockscreen.sh"


def _is_hex(value):
    return len(value) in (6, 8) and all(char in "0123456789abcdefABCDEF" for char in value)


def load_lockscreen_colors(path=LOCKSCREEN):
    colors = []
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = (part.strip() for part in stripped.split("=", 1))
        if not _is_hex(value):
            continue
        rgb = f"#{value[:6]}"
        alpha = value[6:8] if len(value) == 8 else "ff"
        colors.append((name, rgb, alpha))
    return colors


def save_lockscreen_colors(colors, path=LOCKSCREEN):
    updates = {name: (rgb, alpha) for name, rgb, alpha in colors}
    new_lines = []

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            name, _value = (part.strip() for part in stripped.split("=", 1))
            if name in updates:
                rgb, alpha = updates[name]
                new_lines.append(f"{name}={rgb.lstrip('#')}{alpha}")
                continue
        new_lines.append(line)

    path.write_text("\n".join(new_lines) + "\n")
