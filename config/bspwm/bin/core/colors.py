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
