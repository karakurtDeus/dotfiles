import subprocess
import time
from pathlib import Path

from imgui_bundle import ImVec4

POLYBAR_COLORS = Path.home() / ".config" / "polybar" / "colors.ini"
SKIP_COLORS = {"background"}


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


def load_polybar_colors(path=POLYBAR_COLORS):
    colors = []
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")) or "=" not in stripped:
            continue
        name, value = (part.strip() for part in stripped.split("=", 1))
        if name in SKIP_COLORS:
            continue
        colors.append((name, value))
    return colors


def save_polybar_colors(colors, path=POLYBAR_COLORS):
    updates = dict(colors)
    seen = set()
    new_lines = []

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")) or "=" not in stripped:
            new_lines.append(line)
            continue
        name, _value = (part.strip() for part in stripped.split("=", 1))
        if name in updates:
            new_lines.append(f"{name} = {updates[name]}")
            seen.add(name)
        else:
            new_lines.append(line)

    for name, value in colors:
        if name not in seen:
            new_lines.append(f"{name} = {value}")

    path.write_text("\n".join(new_lines) + "\n")


def restart_polybar():
    subprocess.run(["killall", "-q", "polybar"], check=False)
    for _ in range(20):
        running = subprocess.run(
            ["pgrep", "-x", "polybar"],
            stdout=subprocess.DEVNULL,
        )
        if running.returncode != 0:
            break
        time.sleep(0.05)
    subprocess.Popen(
        ["polybar", "down-panel"],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
