from imgui_bundle import imgui, hello_imgui
from control_panel import *
from colors import *

# --------------------------
# VARIABLES
USERNAME = return_username()
KERNEL = kernel_version()
PACKAGES = package_count()
CPU = cpu_name()
GPU = gpu_names()
THEME = get_current_theme()
# --------------------------

# --------------------------
# Control Panel
# --------------------------

def shortcut_link(label):
    clicked = imgui.invisible_button(label, imgui.calc_text_size(label))
    if imgui.is_item_hovered():
        imgui.set_mouse_cursor(imgui.MouseCursor_.hand)
    imgui.get_window_draw_list().add_text(
        imgui.get_item_rect_min(),
        imgui.color_convert_float4_to_u32(GUI_ACCENT),
        label,
    )
    return clicked


def control_panel():
    title = f"Welcome, {USERNAME}!"

    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.push_font(None, imgui.get_style().font_size_base * 1.4)
    imgui.text_colored(GUI_ACCENT, title)
    imgui.pop_font()

    # imgui.new_line()
    # imgui.separator()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "System Information")
    imgui.pop_font()

    imgui.new_line()

    rows = [
        ("Theme:", THEME),
        ("Kernel:", KERNEL),
        ("Packages:", PACKAGES),
        ("CPU:", CPU),
        ("GPU:", GPU),
    ]

    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(GUI_ACCENT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text_colored(GUI_TEXT, str(value))

    imgui.new_line()
    imgui.new_line()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "Quick Settings")
    imgui.pop_font()
    imgui.new_line()

    shortcuts = [
        ("Process manager", ["btop"], False),
        ("Network", ["nmtui"], False),
        ("Bluetooth", ["bluetui"], False),
        ("Audio", ["wpctl", "status"], True),
    ]
    for label, command, hold in shortcuts:
        if shortcut_link(label):
            open_kitty(command, hold)



# --------------------------
# Application
# --------------------------

BACKGROUND = GUI_BG
SURFACES = (
    imgui.Col_.window_bg,
    imgui.Col_.child_bg,
    imgui.Col_.title_bg,
    imgui.Col_.title_bg_active,
    imgui.Col_.title_bg_collapsed,
    imgui.Col_.menu_bar_bg,
    imgui.Col_.docking_empty_bg,
)


def setup_style():
    hello_imgui.imgui_default_settings.setup_default_imgui_style()
    style = imgui.get_style()
    style.tab_bar_border_size = 0
    style.frame_border_size = 0
    style.popup_border_size = 1
    for color in SURFACES:
        style.set_color_(color, BACKGROUND)
    style.set_color_(imgui.Col_.text, GUI_TEXT)
    style.set_color_(imgui.Col_.text_link, GUI_TEXT)
    style.set_color_(imgui.Col_.button, GUI_BUTTON)
    style.set_color_(imgui.Col_.button_hovered, GUI_BUTTON_HOVERED)
    style.set_color_(imgui.Col_.button_active, GUI_BUTTON_ACTIVE)
    style.set_color_(imgui.Col_.frame_bg, GUI_FRAME)
    style.set_color_(imgui.Col_.frame_bg_hovered, GUI_FRAME_HOVERED)
    style.set_color_(imgui.Col_.frame_bg_active, GUI_FRAME_ACTIVE)
    style.set_color_(imgui.Col_.tab, GUI_TAB)
    style.set_color_(imgui.Col_.tab_hovered, GUI_TAB_HOVERED)
    style.set_color_(imgui.Col_.tab_selected, GUI_TAB_SELECTED)
    style.set_color_(imgui.Col_.tab_dimmed, GUI_TAB)
    style.set_color_(imgui.Col_.tab_dimmed_selected, GUI_TAB_SELECTED)
    style.set_color_(imgui.Col_.popup_bg, GUI_POPUP)
    style.set_color_(imgui.Col_.border, GUI_POPUP_BORDER)
    style.set_color_(imgui.Col_.header, GUI_HEADER)
    style.set_color_(imgui.Col_.header_hovered, GUI_HEADER_HOVERED)
    style.set_color_(imgui.Col_.header_active, GUI_HEADER_ACTIVE)
    style.set_color_(imgui.Col_.check_mark, GUI_ACCENT)
    style.set_color_(imgui.Col_.slider_grab, GUI_ACCENT)
    style.set_color_(imgui.Col_.slider_grab_active, GUI_ACCENT)


def cheatsheet_panel():
    title = "Cheatsheet"

    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.push_font(None, imgui.get_style().font_size_base * 1.4)
    imgui.text_colored(GUI_ACCENT, title)
    imgui.pop_font()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "Rofi")
    imgui.pop_font()

    imgui.new_line()

    rows = [
        ("App manager:", "super + space"),
        ("Buffer manager:", "super + v"),
        ("Power menu:", "super + ctrl + p"),
        ("Wallpaper selector:", "super + ctrl + w"),
        ("Script manager:", "super + ctrl + space"),
    ]
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(GUI_ACCENT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text(str(value))

    imgui.new_line()
    imgui.new_line()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "General")
    imgui.pop_font()

    imgui.new_line()

    rows = [
        ("Reload bspwm:", "super + alt + r"),
        ("Reload sxhkd:", "super + Escape"),
        ("File manager:", "super + e"),
        ("Terminal:", "super + Enter"),
    ]
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(GUI_ACCENT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text(str(value))

    imgui.new_line()
    imgui.new_line()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "Quick settings")
    imgui.pop_font()

    imgui.new_line()

    rows = [
        ("Network manager:", "nmtui"),
        ("Bluethooth:", "bluetui"),
        ("Audio:", "wpctl status && wpctl set-default <device>"),
    ]
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(GUI_ACCENT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text(str(value))

def appearance_panel():
    title = "Appearance"

    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.push_font(None, imgui.get_style().font_size_base * 1.4)
    imgui.text_colored(GUI_ACCENT, title)
    imgui.pop_font()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "BSPWM window")
    imgui.pop_font()

    imgui.new_line()

    _, values = current_bspwm_settings()
    if values:
        labels = [(key, key.replace("_", " ").capitalize() + ":") for key in values]
        label_width = max(imgui.calc_text_size(label).x for _, label in labels)
        gap = imgui.calc_text_size("    ").x
        origin_x = imgui.get_cursor_pos_x()

        for key, label in labels:
            imgui.text_colored(GUI_ACCENT, label)
            imgui.same_line()
            imgui.set_cursor_pos_x(origin_x + label_width + gap)
            imgui.set_next_item_width(140)
            changed, new_value = imgui.input_int(f"##{key}", values[key])
            if changed:
                set_bspwm_setting(key, new_value)

    imgui.new_line()
    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "Picom")
    imgui.pop_font()
    imgui.new_line()

    settings = current_picom_settings()
    picom_labels = [
        "Backend:",
        "vSync:",
        "Corner radius:",
        "Shadows:",
        "Shadow color:",
        "Fading:",
        "Blur:",
        "Animations:",
        "Opacity:",
        "Level:",
    ]
    backends = ["glx", "egl", "xrender"]
    label_width = max(imgui.calc_text_size(label).x for label in picom_labels)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    def edit_picom(label, key, draw, live=False):
        imgui.text_colored(GUI_ACCENT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.set_next_item_width(180)
        changed, value = draw(settings[key])
        if changed:
            settings[key] = value
        if (live and changed) or imgui.is_item_deactivated_after_edit():
            apply_picom_settings()

    def draw_color(value):
        changed, color = imgui.color_edit3(
            "##shadow-color",
            hex_to_color(value),
            imgui.ColorEditFlags_.display_hex | imgui.ColorEditFlags_.no_options,
        )
        return changed, color_to_hex(color) if changed else value

    def draw_backend(value):
        index = backends.index(value) if value in backends else 0
        changed, index = imgui.combo("##backend", index, backends)
        return changed, backends[index]

    edit_picom("Backend:", "backend", draw_backend, live=True)
    edit_picom("vSync:", "vsync", lambda v: imgui.checkbox("##vsync", v), live=True)
    edit_picom("Corner radius:", "corner_radius", lambda v: imgui.slider_int("##corner-radius", v, 0, 99))
    edit_picom("Shadows:", "shadow", lambda v: imgui.checkbox("##shadow", v), live=True)
    edit_picom("Shadow color:", "shadow_color", draw_color)
    edit_picom("Fading:", "fading", lambda v: imgui.slider_int("##fading", v, 0, 100))
    edit_picom("Blur:", "blur", lambda v: imgui.checkbox("##blur", v), live=True)
    edit_picom("Animations:", "animations", lambda v: imgui.checkbox("##animations", v), live=True)
    edit_picom("Opacity:", "opacity_enabled", lambda v: imgui.checkbox("##opacity", v), live=True)
    edit_picom("Level:", "opacity", lambda v: imgui.slider_int("##opacity-level", v, 15, 100))

    apps = system_apps()
    labels = [label for label, _klass in apps]
    if not hasattr(appearance_panel, "exclude_index"):
        appearance_panel.exclude_index = 0
    imgui.text_colored(GUI_ACCENT, "Exclude:")
    imgui.same_line()
    imgui.set_cursor_pos_x(origin_x + label_width + gap)
    imgui.set_next_item_width(220)
    if labels:
        appearance_panel.exclude_index = min(appearance_panel.exclude_index, len(labels) - 1)
        _changed, appearance_panel.exclude_index = imgui.combo(
            "##opacity-exclude",
            appearance_panel.exclude_index,
            labels,
            12,
        )
        imgui.same_line()
        if imgui.button("Add"):
            klass = apps[appearance_panel.exclude_index][1]
            if klass not in settings["opacity_exclude"]:
                settings["opacity_exclude"].append(klass)
                apply_picom_settings()
    for klass in list(settings["opacity_exclude"]):
        imgui.text_colored(GUI_TEXT, klass)
        imgui.same_line()
        if imgui.button(f"Remove##{klass}"):
            settings["opacity_exclude"].remove(klass)
            apply_picom_settings()

    imgui.new_line()
    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "Dunst")
    imgui.pop_font()
    imgui.new_line()

    dunst = current_dunst_settings()
    fonts = list(system_fonts())
    if dunst["family"] and dunst["family"] not in fonts:
        fonts.insert(0, dunst["family"])

    color_rows = [(dunst_color_label(section, key), section, key) for section, key in dunst["order"]]
    dunst_labels = (
        ["Font:", "Size:", "Border:", "Border size:"]
        + [field[2] for field in DUNST_FIELDS]
        + [label for _section, label in DUNST_TIMEOUTS]
        + [label for label, _, _ in color_rows]
    )
    label_width = max(imgui.calc_text_size(label).x for label in dunst_labels)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    imgui.text_colored(GUI_ACCENT, "Font:")
    imgui.same_line()
    imgui.set_cursor_pos_x(origin_x + label_width + gap)
    imgui.set_next_item_width(300)
    if fonts:
        index = fonts.index(dunst["family"]) if dunst["family"] in fonts else 0
        changed, index = imgui.combo("##dunst-font", index, fonts, 12)
        if changed:
            dunst["family"] = fonts[index]
            apply_dunst_settings()

    imgui.text_colored(GUI_ACCENT, "Size:")
    imgui.same_line()
    imgui.set_cursor_pos_x(origin_x + label_width + gap)
    imgui.set_next_item_width(300)
    size = int(dunst["size"]) if str(dunst["size"]).isdigit() else 11
    changed, size = imgui.slider_int("##dunst-size", size, 6, 48)
    if changed:
        dunst["size"] = str(size)
    if imgui.is_item_deactivated_after_edit():
        apply_dunst_settings()

    def dunst_control(label):
        imgui.text_colored(GUI_ACCENT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.set_next_item_width(300)

    for field in DUNST_FIELDS:
        kind, key, label = field[0], field[1], field[2]
        dunst_control(label)
        if kind == "int":
            low, high = field[3], field[4]
            changed, value = imgui.slider_int(f"##dunst-{key}", int(dunst["ints"][key]), low, high)
            if changed:
                dunst["ints"][key] = value
            if imgui.is_item_deactivated_after_edit():
                apply_dunst_settings()
        else:
            options = list(field[3])
            current = dunst["strs"][key]
            if current not in options:
                options.insert(0, current)
            index = options.index(current)
            changed, index = imgui.combo(f"##dunst-{key}", index, options, 8)
            if changed:
                dunst["strs"][key] = options[index]
                apply_dunst_settings()

    for section, label in DUNST_TIMEOUTS:
        dunst_control(label)
        changed, value = imgui.slider_int(
            f"##dunst-timeout-{section}",
            int(dunst["timeouts"][section]),
            0,
            120,
        )
        if changed:
            dunst["timeouts"][section] = value
        if imgui.is_item_deactivated_after_edit():
            apply_dunst_settings()

    imgui.text_colored(GUI_ACCENT, "Border:")
    imgui.same_line()
    imgui.set_cursor_pos_x(origin_x + label_width + gap)
    enabled = int(dunst["frame_width"]) > 0
    changed, enabled = imgui.checkbox("##dunst-border", enabled)
    if changed:
        if enabled:
            dunst["frame_width"] = int(dunst["frame_width_on"]) or 2
        else:
            if int(dunst["frame_width"]) > 0:
                dunst["frame_width_on"] = int(dunst["frame_width"])
            dunst["frame_width"] = 0
        apply_dunst_settings()

    imgui.text_colored(GUI_ACCENT, "Border size:")
    imgui.same_line()
    imgui.set_cursor_pos_x(origin_x + label_width + gap)
    imgui.set_next_item_width(300)
    border_size = int(dunst["frame_width_on"]) or 2
    changed, border_size = imgui.slider_int("##dunst-border-size", border_size, 1, 16)
    if changed:
        dunst["frame_width_on"] = border_size
        if int(dunst["frame_width"]) > 0:
            dunst["frame_width"] = border_size
    if imgui.is_item_deactivated_after_edit() and int(dunst["frame_width"]) > 0:
        apply_dunst_settings()

    for label, section, key in color_rows:
        imgui.text_colored(GUI_ACCENT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.set_next_item_width(300)
        changed, color = imgui.color_edit3(
            f"##dunst-{section}-{key}",
            hex_to_color(dunst["colors"][(section, key)]),
            imgui.ColorEditFlags_.display_hex | imgui.ColorEditFlags_.no_options,
        )
        if changed:
            dunst["colors"][(section, key)] = color_to_hex(color)
        if imgui.is_item_deactivated_after_edit():
            apply_dunst_settings()

    kitty = current_kitty_settings()
    if kitty["order"]:
        imgui.new_line()
        imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
        imgui.text_colored(GUI_ACCENT, "Kitty")
        imgui.pop_font()
        imgui.new_line()

        kitty_labels = [KITTY_LABELS[key] for key in kitty["order"]]
        label_width = max(imgui.calc_text_size(label).x for label in kitty_labels)
        gap = imgui.calc_text_size("    ").x
        origin_x = imgui.get_cursor_pos_x()

        def kitty_control(label, width=True):
            imgui.text_colored(GUI_ACCENT, label)
            imgui.same_line()
            imgui.set_cursor_pos_x(origin_x + label_width + gap)
            if width:
                imgui.set_next_item_width(300)

        for key in kitty["order"]:
            label = KITTY_LABELS[key]
            value = kitty["values"][key]
            wide = key not in ("enable_audio_bell", "window_alert_on_bell", "confirm_os_window_close")
            kitty_control(label, wide)
            if key in ("enable_audio_bell", "window_alert_on_bell", "confirm_os_window_close"):
                enabled = kitty_yes(value) if key != "confirm_os_window_close" else kitty_confirm(value)
                changed, enabled = imgui.checkbox(f"##kitty-{key}", enabled)
                if changed:
                    if key == "confirm_os_window_close":
                        kitty["values"][key] = "1" if enabled else "0"
                    else:
                        kitty["values"][key] = "yes" if enabled else "no"
                    apply_kitty_settings()
            elif key in ("background", "foreground") and value.startswith("#") and len(value) == 7:
                changed, color = imgui.color_edit3(
                    f"##kitty-{key}",
                    hex_to_color(value),
                    imgui.ColorEditFlags_.display_hex | imgui.ColorEditFlags_.no_options,
                )
                if changed:
                    kitty["values"][key] = color_to_hex(color)
                if imgui.is_item_deactivated_after_edit():
                    apply_kitty_settings()
            elif key == "visual_bell_duration":
                changed, seconds = imgui.slider_float(f"##kitty-{key}", kitty_seconds(value), 0.0, 10.0, "%.1f")
                if changed:
                    kitty["values"][key] = kitty_seconds_text(value, seconds)
                if imgui.is_item_deactivated_after_edit():
                    apply_kitty_settings()
            elif key == "font_size":
                changed, size = imgui.slider_int(f"##kitty-{key}", int(kitty_seconds(value)), 6, 32)
                if changed:
                    kitty["values"][key] = str(size)
                if imgui.is_item_deactivated_after_edit():
                    apply_kitty_settings()

    theme = current_theme_colors()

    def draw_theme_group(title, fields):
        rows = [(key, label) for key, label in fields if key in theme]
        if not rows:
            return
        imgui.new_line()
        imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
        imgui.text_colored(GUI_ACCENT, title)
        imgui.pop_font()
        imgui.new_line()
        label_width = max(imgui.calc_text_size(label).x for _key, label in rows)
        gap = imgui.calc_text_size("    ").x
        origin_x = imgui.get_cursor_pos_x()
        for key, label in rows:
            imgui.text_colored(GUI_ACCENT, label)
            imgui.same_line()
            imgui.set_cursor_pos_x(origin_x + label_width + gap)
            imgui.set_next_item_width(300)
            changed, color = imgui.color_edit3(
                f"##theme-{key}",
                hex_to_color(theme[key]),
                imgui.ColorEditFlags_.display_hex | imgui.ColorEditFlags_.no_options,
            )
            if changed:
                theme[key] = color_to_hex(color)
            if imgui.is_item_deactivated_after_edit():
                apply_theme_colors()
                if key.startswith("control_panel_"):
                    setup_style()

    draw_theme_group("Lockscreen", LOCKSCREEN_FIELDS)
    draw_theme_group("Control panel", PANEL_FIELDS)

    rofi = current_rofi_colors()
    if any(rofi["files"].values()):
        imgui.new_line()
        imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
        imgui.text_colored(GUI_ACCENT, "Rofi")
        imgui.pop_font()
        imgui.text_colored(GUI_TEXT, rofi["theme"])

        def draw_rofi_group(title, name):
            colors = rofi["files"].get(name, {})
            rows = [(key, ROFI_LABELS[key]) for key in ROFI_LABELS if key in colors]
            if not rows:
                return
            imgui.new_line()
            imgui.text_colored(GUI_ACCENT, title)
            imgui.new_line()
            label_width = max(imgui.calc_text_size(label).x for _key, label in rows)
            gap = imgui.calc_text_size("    ").x
            origin_x = imgui.get_cursor_pos_x()
            for key, label in rows:
                imgui.text_colored(GUI_ACCENT, label)
                imgui.same_line()
                imgui.set_cursor_pos_x(origin_x + label_width + gap)
                imgui.set_next_item_width(300)
                changed, color = imgui.color_edit3(
                    f"##rofi-{name}-{key}",
                    hex_to_color(colors[key]),
                    imgui.ColorEditFlags_.display_hex | imgui.ColorEditFlags_.no_options,
                )
                if changed:
                    colors[key] = color_to_hex(color)
                if imgui.is_item_deactivated_after_edit():
                    apply_rofi_colors()

        draw_rofi_group("Powermenu", "powermenu")
        draw_rofi_group("Select", "select")
        draw_rofi_group("Drun", "drun")

    btop = current_btop_colors()
    if btop:
        imgui.new_line()
        imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
        imgui.text_colored(GUI_ACCENT, "Btop")
        imgui.pop_font()

        def draw_btop_group(title, fields):
            rows = [(key, label) for key, label in fields if key in btop]
            if not rows:
                return
            imgui.new_line()
            imgui.text_colored(GUI_ACCENT, title)
            imgui.new_line()
            label_width = max(imgui.calc_text_size(label).x for _key, label in rows)
            gap = imgui.calc_text_size("    ").x
            origin_x = imgui.get_cursor_pos_x()
            for key, label in rows:
                imgui.text_colored(GUI_ACCENT, label)
                imgui.same_line()
                imgui.set_cursor_pos_x(origin_x + label_width + gap)
                imgui.set_next_item_width(300)
                changed, color = imgui.color_edit3(
                    f"##btop-{key}",
                    hex_to_color(btop[key]),
                    imgui.ColorEditFlags_.display_hex | imgui.ColorEditFlags_.no_options,
                )
                if changed:
                    btop[key] = color_to_hex(color)
                if imgui.is_item_deactivated_after_edit():
                    apply_btop_colors()

        for title, fields in BTOP_GROUPS:
            draw_btop_group(title, fields)

def autostart_panel():
    title = "Autostart"
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.push_font(None, imgui.get_style().font_size_base * 1.4)
    imgui.text_colored(GUI_ACCENT, title)
    imgui.pop_font()
    imgui.text_colored(GUI_TEXT, get_current_theme())
    imgui.new_line()

    entries = current_autostart()
    apps = desktop_apps()
    if not hasattr(autostart_panel, "app_index"):
        autostart_panel.app_index = 0
        autostart_panel.window_index = 0
        autostart_panel.url = ""
        autostart_panel.windows = open_windows()
        autostart_panel.desks = desktop_count()
    windows = autostart_panel.windows
    desks = autostart_panel.desks

    labels = [app["name"] if app["name"] == app["class"] else f"{app['name']} ({app['class']})" for app in apps]
    imgui.text_colored(GUI_ACCENT, "App:")
    imgui.same_line()
    imgui.set_next_item_width(280)
    if labels:
        autostart_panel.app_index = min(autostart_panel.app_index, len(labels) - 1)
        _changed, autostart_panel.app_index = imgui.combo("##autostart-app", autostart_panel.app_index, labels, 12)
        imgui.same_line()
        if imgui.button("Add"):
            app = apps[autostart_panel.app_index]
            if not any(entry["class"] == app["class"] and not entry["url"] for entry in entries):
                entries.append({
                    "class": app["class"],
                    "exec": app["exec"],
                    "url": "",
                    "desktop": 1,
                    "floating": False,
                    "x": 0,
                    "y": 0,
                    "w": 0,
                    "h": 0,
                    "sw": 0,
                    "sh": 0,
                })
                save_autostart()

    imgui.text_colored(GUI_ACCENT, "Link:")
    imgui.same_line()
    imgui.set_next_item_width(280)
    _changed, autostart_panel.url = imgui.input_text("##autostart-url", autostart_panel.url)
    imgui.same_line()
    if imgui.button("Add##link") and autostart_panel.url.strip():
        entries.append({
            "class": "",
            "exec": "",
            "url": autostart_panel.url.strip(),
            "desktop": 1,
            "floating": False,
            "x": 0,
            "y": 0,
            "w": 0,
            "h": 0,
            "sw": 0,
            "sh": 0,
        })
        autostart_panel.url = ""
        save_autostart()

    window_labels = []
    for window in windows:
        name = window.get("title") or window["class"]
        if len(name) > 48:
            name = name[:45] + "..."
        window_labels.append(
            f"{name}  {window['desktop']}  {'floating' if window['floating'] else 'tiled'}"
        )
    if window_labels:
        imgui.text_colored(GUI_ACCENT, "Window:")
        imgui.same_line()
        imgui.set_next_item_width(280)
        autostart_panel.window_index = min(autostart_panel.window_index, len(window_labels) - 1)
        _changed, autostart_panel.window_index = imgui.combo(
            "##autostart-window", autostart_panel.window_index, window_labels, 8
        )
        imgui.same_line()
        if imgui.button("Refresh"):
            autostart_panel.windows = open_windows()
            autostart_panel.desks = desktop_count()
        imgui.same_line()
        if imgui.button("Capture"):
            entry = entry_from_window(windows[autostart_panel.window_index])
            replaced = False
            for index, current in enumerate(entries):
                if not current["class"] or current["class"] != entry["class"]:
                    continue
                if current["desktop"] != entry["desktop"]:
                    continue
                current_title = current.get("title") or ""
                if current_title in ("", entry.get("title") or ""):
                    entries[index] = entry
                    replaced = True
                    break
            if not replaced:
                entries.append(entry)
            save_autostart()

    imgui.new_line()
    for index, entry in enumerate(list(entries)):
        title = entry["url"] or entry.get("title") or entry["class"] or entry["exec"]
        imgui.text_colored(GUI_ACCENT, title)
        if entry["exec"] and not entry["url"]:
            imgui.same_line()
            imgui.text_colored(GUI_TEXT, entry["exec"])
        imgui.same_line()
        if imgui.button(f"Remove##autostart-{index}"):
            entries.pop(index)
            save_autostart()
            continue
        imgui.text_colored(GUI_ACCENT, "Desktop:")
        imgui.same_line()
        imgui.set_next_item_width(120)
        changed, desk = imgui.slider_int(f"##autostart-desk-{index}", int(entry["desktop"]), 1, desks)
        if changed:
            entry["desktop"] = desk
        if imgui.is_item_deactivated_after_edit():
            save_autostart()
        imgui.same_line()
        changed, floating = imgui.checkbox(f"Floating##autostart-{index}", entry["floating"])
        if changed:
            entry["floating"] = floating
            save_autostart()
        if entry["floating"]:
            for key, label in (("x", "X"), ("y", "Y"), ("w", "W"), ("h", "H")):
                imgui.text_colored(GUI_ACCENT, f"{label}:")
                imgui.same_line()
                imgui.set_next_item_width(90)
                changed, value = imgui.input_int(f"##autostart-{key}-{index}", int(entry[key]))
                if changed:
                    entry[key] = value
                if imgui.is_item_deactivated_after_edit():
                    save_autostart()
                imgui.same_line()
            if entry.get("sw") and entry.get("sh"):
                imgui.text_colored(GUI_TEXT, f"{int(entry['sw'])}x{int(entry['sh'])}")
            imgui.new_line()


def main():

    params = hello_imgui.RunnerParams()

    params.app_window_params.window_title = "Arch Control Panel"

    params.app_window_params.window_geometry.size = (900, 600)

    # Enable docking
    params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )

    params.ini_disable = True
    params.ini_clear_previous_settings = True
    params.docking_params.layout_condition = (
        hello_imgui.DockingLayoutCondition.application_start
    )
    params.imgui_window_params.background_color = BACKGROUND
    params.callbacks.setup_imgui_style = setup_style

    def show_gui():
        # The last docked window takes focus on the first frame.
        if show_gui.frame == 1:
            params.docking_params.focus_dockable_window("Control Panel")
        show_gui.frame += 1

    show_gui.frame = 0
    params.callbacks.show_gui = show_gui

    # Window list
    windows = [
        ("Control Panel", control_panel),
        ("Appearance", appearance_panel),
        ("Autostart", autostart_panel),
        ("Cheatsheet", cheatsheet_panel),
    ]

    dockable_windows = []

    for name, function in windows:

        window = hello_imgui.DockableWindow()

        window.label = name

        window.dock_space_name = "MainDockSpace"

        window.gui_function = function

        window.can_be_closed = False

        dockable_windows.append(window)

    # IMPORTANT: pass the whole list at once
    params.docking_params.dockable_windows = dockable_windows

    # Run the application
    hello_imgui.run(params)


if __name__ == "__main__":
    main()