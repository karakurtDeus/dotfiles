
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
GUI_BG = hex_to_color("#161117")
GUI_ACCENT = hex_to_color("#D9ADE8")
# --------------------------

# --------------------------
# TEXT
GUI_TEXT = hex_to_color("#DBD6DD")
GUI_BUTTON_TEXT = hex_to_color("#DBD6DD")
# --------------------------

# --------------------------
# BUTTONS
GUI_BUTTON = hex_to_color("#1B191C")
GUI_BUTTON_HOVERED = hex_to_color("#4B3E50")
GUI_BUTTON_ACTIVE = hex_to_color("#4B3E50")
# --------------------------

# --------------------------
# INPUTS
GUI_FRAME = hex_to_color("#1B191C")
GUI_FRAME_HOVERED = hex_to_color("#1B191C")
GUI_FRAME_ACTIVE = hex_to_color("#1B191C")
# --------------------------

# --------------------------
# TAB BAR
GUI_TAB = hex_to_color("#1B191C")
GUI_TAB_HOVERED = hex_to_color("#4A3D50")
GUI_TAB_SELECTED = hex_to_color("#4A3D50")
# --------------------------

# --------------------------
# POPUP
GUI_POPUP = hex_to_color("#1B191C")
GUI_POPUP_BORDER = hex_to_color("#4A3D50")
GUI_HEADER = hex_to_color("#4A3D50")
GUI_HEADER_HOVERED = hex_to_color("#4A3D50")
GUI_HEADER_ACTIVE = hex_to_color("#4A3D50")
# --------------------------