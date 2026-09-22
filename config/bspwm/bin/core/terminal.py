from pathlib import Path


KITTY_CONF = Path.home() / ".config" / "kitty" / "kitty.conf"


def get_terminal_settings(config=KITTY_CONF):
    for line in config.read_text().splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] == "background":
            return parts[1]

    return None


def set_background(hex_color, config=KITTY_CONF):
    text = config.read_text()
    lines = text.splitlines()
    updated = False
    new_lines = []

    for line in lines:
        parts = line.split()
        if parts and parts[0] == "background":
            new_lines.append(f"background {hex_color}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"background {hex_color}")

    config.write_text("\n".join(new_lines) + "\n")
