import subprocess
from pathlib import Path


DUNST_RC = Path.home() / ".config" / "dunst" / "dunstrc"

# Panel label -> dunstrc section. Background is shared across all of them.
ALERTS = (
    ("light", "urgency_low"),
    ("normal", "urgency_normal"),
    ("error", "urgency_critical"),
)
SECTION_LABELS = {section: label for label, section in ALERTS}


def _unquote(value):
    return value.strip().strip('"').strip("'")


def load_dunst_colors(path=DUNST_RC):
    section = None
    background = None
    foregrounds = {}

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1].strip()
            continue
        if section not in SECTION_LABELS:
            continue
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = (part.strip() for part in stripped.split("=", 1))
        if key == "background" and background is None:
            background = _unquote(value)
        elif key == "foreground":
            foregrounds[SECTION_LABELS[section]] = _unquote(value)

    alerts = [(label, foregrounds[label]) for label, _section in ALERTS if label in foregrounds]
    return background, alerts


def save_dunst_colors(background, alerts, path=DUNST_RC):
    foregrounds = dict(alerts)
    section = None
    new_lines = []

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1].strip()
            new_lines.append(line)
            continue

        label = SECTION_LABELS.get(section)
        if label and stripped and not stripped.startswith("#") and "=" in stripped:
            key, _value = (part.strip() for part in stripped.split("=", 1))
            indent = line[: len(line) - len(line.lstrip())]
            if key == "background":
                new_lines.append(f'{indent}background = "{background}"')
                continue
            if key == "foreground" and label in foregrounds:
                new_lines.append(f'{indent}foreground = "{foregrounds[label]}"')
                continue

        new_lines.append(line)

    path.write_text("\n".join(new_lines) + "\n")


def reload_dunst():
    result = subprocess.run(
        ["dunstctl", "reload"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        subprocess.Popen(
            ["dunst"],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
