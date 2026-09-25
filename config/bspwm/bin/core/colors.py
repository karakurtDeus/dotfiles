
from imgui_bundle import ImVec4

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

# --------------------------
# BACKGROUND COLORS
GUI_BG = hex_to_color("#000000")
GUI_ACCENT = hex_to_color("#F0C674")
# --------------------------

# --------------------------
# TEXT
GUI_TEXT = hex_to_color("#FFFFFF")
GUI_BUTTON_TEXT = hex_to_color("#F0C674")
# --------------------------

# --------------------------
# BUTTONS
GUI_BUTTON = hex_to_color("#000000")
GUI_BUTTON_HOVERED = hex_to_color("#1A1A1A")
GUI_BUTTON_ACTIVE = hex_to_color("#F0C674")
# --------------------------

# --------------------------
# TAB BAR
GUI_TAB = hex_to_color("#000000")
GUI_TAB_HOVERED = hex_to_color("#1A1A1A")
GUI_TAB_SELECTED = hex_to_color("#000000")
# --------------------------