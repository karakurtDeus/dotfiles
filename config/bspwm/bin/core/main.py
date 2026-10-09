import time
from pathlib import Path

from imgui_bundle import imgui, hello_imgui
from imgui_bundle.immapp import icons_fontawesome_4 as icons
from control_panel import *
from colors import *

# --------------------------
# VARIABLES
USERNAME = return_username()
KERNEL = kernel_version()
PACKAGES = package_count()
CPU = cpu_name()
GPU = gpu_names()
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
        ("Theme:", get_current_theme()),
        ("Kernel:", KERNEL),
        ("Packages:", PACKAGES),
        ("CPU:", CPU),
        ("GPU:", GPU),
    ]

    begin_fields("##fields-system")
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(GUI_TEXT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text_colored(GUI_TEXT, str(value))
    end_fields()

    imgui.new_line()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "Controls")
    imgui.pop_font()
    imgui.new_line()

    if not hasattr(control_panel, "devices"):
        control_panel.devices = {
            "brightness": read_brightness(),
            **read_audio(),
        }
        control_panel.devices_at = 0.0
        control_panel.hold_devices = 0.0
    devices = control_panel.devices
    now = time.time()
    slider_active = False

    device_labels = ["Brightness:", "Volume:", "Mute audio:", "Mute microphone:"]
    begin_fields("##fields-controls")
    label_width = max(imgui.calc_text_size(label).x for label in device_labels)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    def device_row(label):
        imgui.text_colored(GUI_TEXT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)

    if devices["brightness"] is not None:
        device_row("Brightness:")
        imgui.set_next_item_width(220)
        changed, level = imgui.slider_int("##brightness", int(devices["brightness"]), 1, 100)
        if changed:
            devices["brightness"] = level
            set_brightness(level)
            control_panel.hold_devices = now + 0.4
        slider_active = slider_active or imgui.is_item_active()

    device_row("Volume:")
    imgui.set_next_item_width(220)
    changed, level = imgui.slider_int("##volume", int(devices["volume"]), 0, 100)
    if changed:
        devices["volume"] = level
        devices["sink_mute"] = False
        set_volume(level)
        control_panel.hold_devices = now + 0.4
    slider_active = slider_active or imgui.is_item_active()

    device_row("Mute audio:")
    changed, muted = imgui.checkbox("##mute-audio", devices["sink_mute"])
    if changed:
        devices["sink_mute"] = muted
        set_muted("sink", muted)
        control_panel.hold_devices = now + 0.4

    device_row("Mute microphone:")
    changed, muted = imgui.checkbox("##mute-mic", devices["source_mute"])
    if changed:
        devices["source_mute"] = muted
        set_muted("source", muted)
        control_panel.hold_devices = now + 0.4

    if not slider_active and now >= control_panel.hold_devices and now - control_panel.devices_at >= 0.4:
        fresh_brightness = read_brightness()
        if fresh_brightness is not None:
            devices["brightness"] = fresh_brightness
        devices.update(read_audio())
        control_panel.devices_at = now
    end_fields()

    imgui.new_line()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "Quick Settings")
    imgui.pop_font()
    imgui.new_line()

    begin_fields("##fields-shortcuts")
    shortcuts = [
        ("Process manager", ["btop"], False),
        ("Network", ["nmtui"], False),
        ("Bluetooth", ["bluetui"], False),
        ("Audio", ["wpctl", "status"], True),
    ]
    for label, command, hold in shortcuts:
        if shortcut_link(label):
            open_kitty(command, hold)
    end_fields()



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
    style.frame_rounding = 6
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
    begin_fields("##fields-cheat-rofi")
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(GUI_TEXT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text(str(value))
    end_fields()

    imgui.new_line()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "Kitty")
    imgui.pop_font()

    imgui.new_line()

    rows = [
        ("New split:", "ctrl + shift + enter"),
        ("Next split:", "ctrl + shift + ]"),
        ("Previous split:", "ctrl + shift + ["),
        ("Resize split:", "ctrl + shift + r"),
        ("Close split:", "ctrl + shift + w"),
    ]
    begin_fields("##fields-cheat-kitty")
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(GUI_TEXT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text(str(value))
    end_fields()

    imgui.new_line()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "Bspwm")
    imgui.pop_font()

    imgui.new_line()

    rows = [
        ("Focus:", "super + h j k l"),
        ("Swap window:", "super + shift + h j k l"),
        ("Place next:", "super + ctrl + h j k l"),
        ("Place ratio:", "super + ctrl + 1-9"),
        ("Grow:", "super + alt + h j k l"),
        ("Shrink:", "super + alt + shift + h j k l"),
    ]
    begin_fields("##fields-cheat-bspwm")
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(GUI_TEXT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text(str(value))
    end_fields()

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
    begin_fields("##fields-cheat-general")
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(GUI_TEXT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text(str(value))
    end_fields()

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
    begin_fields("##fields-cheat-quick")
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(GUI_TEXT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text(str(value))
    end_fields()

def group_fill():
    blend = 0.55
    return imgui.ImVec4(
        GUI_BG.x + (GUI_FRAME.x - GUI_BG.x) * blend,
        GUI_BG.y + (GUI_FRAME.y - GUI_BG.y) * blend,
        GUI_BG.z + (GUI_FRAME.z - GUI_BG.z) * blend,
        1.0,
    )


def begin_fields(name):
    imgui.push_style_color(imgui.Col_.child_bg, group_fill())
    imgui.push_style_var(imgui.StyleVar_.child_rounding, 12)
    imgui.push_style_var(imgui.StyleVar_.window_padding, imgui.ImVec2(12, 10))
    imgui.begin_child(
        name,
        imgui.ImVec2(0, 0),
        imgui.ChildFlags_.auto_resize_y
        | imgui.ChildFlags_.always_auto_resize
        | imgui.ChildFlags_.always_use_window_padding,
    )


def end_fields():
    imgui.end_child()
    imgui.pop_style_var(2)
    imgui.pop_style_color()


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
        begin_fields("##fields-bspwm")
        labels = [(key, key.replace("_", " ").capitalize() + ":") for key in values]
        label_width = max(imgui.calc_text_size(label).x for _, label in labels)
        gap = imgui.calc_text_size("    ").x
        origin_x = imgui.get_cursor_pos_x()

        for key, label in labels:
            imgui.text_colored(GUI_TEXT, label)
            imgui.same_line()
            imgui.set_cursor_pos_x(origin_x + label_width + gap)
            imgui.set_next_item_width(140)
            changed, new_value = imgui.input_int(f"##{key}", values[key])
            if changed:
                set_bspwm_setting(key, new_value)
        end_fields()

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
    begin_fields("##fields-picom")
    label_width = max(imgui.calc_text_size(label).x for label in picom_labels)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    def edit_picom(label, key, draw, live=False):
        imgui.text_colored(GUI_TEXT, label)
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
        imgui.text_colored(GUI_TEXT, "Exclude:")
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
    end_fields()

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
    begin_fields("##fields-dunst")
    label_width = max(imgui.calc_text_size(label).x for label in dunst_labels)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    imgui.text_colored(GUI_TEXT, "Font:")
    imgui.same_line()
    imgui.set_cursor_pos_x(origin_x + label_width + gap)
    imgui.set_next_item_width(300)
    if fonts:
        index = fonts.index(dunst["family"]) if dunst["family"] in fonts else 0
        changed, index = imgui.combo("##dunst-font", index, fonts, 12)
        if changed:
            dunst["family"] = fonts[index]
            apply_dunst_settings()

    imgui.text_colored(GUI_TEXT, "Size:")
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
        imgui.text_colored(GUI_TEXT, label)
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

    imgui.text_colored(GUI_TEXT, "Border:")
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

    imgui.text_colored(GUI_TEXT, "Border size:")
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
        imgui.text_colored(GUI_TEXT, label)
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
    end_fields()

    kitty = current_kitty_settings()
    if kitty["order"]:
        imgui.new_line()
        imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
        imgui.text_colored(GUI_ACCENT, "Kitty")
        imgui.pop_font()
        imgui.new_line()

        begin_fields("##fields-kitty")
        kitty_labels = [KITTY_LABELS[key] for key in kitty["order"]]
        label_width = max(imgui.calc_text_size(label).x for label in kitty_labels)
        gap = imgui.calc_text_size("    ").x
        origin_x = imgui.get_cursor_pos_x()

        def kitty_control(label, width=True):
            imgui.text_colored(GUI_TEXT, label)
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
            elif key in ("background", "foreground", "active_border_color", "inactive_border_color") and value.startswith("#") and len(value) == 7:
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
        end_fields()

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
        begin_fields(f"##fields-theme-{title}")
        label_width = max(imgui.calc_text_size(label).x for _key, label in rows)
        gap = imgui.calc_text_size("    ").x
        origin_x = imgui.get_cursor_pos_x()
        for key, label in rows:
            imgui.text_colored(GUI_TEXT, label)
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
        end_fields()

    draw_theme_group("Lockscreen", LOCKSCREEN_FIELDS)
    draw_theme_group("Control panel", PANEL_FIELDS)

    rofi = current_rofi_colors()
    if any(rofi["files"].values()):
        imgui.new_line()
        imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
        imgui.text_colored(GUI_ACCENT, "Rofi")
        imgui.pop_font()

        def draw_rofi_group(title, name):
            colors = rofi["files"].get(name, {})
            rows = [(key, ROFI_LABELS[key]) for key in ROFI_LABELS if key in colors]
            if not rows:
                return
            imgui.new_line()
            imgui.text_colored(GUI_ACCENT, title)
            imgui.new_line()
            begin_fields(f"##fields-rofi-{name}")
            label_width = max(imgui.calc_text_size(label).x for _key, label in rows)
            gap = imgui.calc_text_size("    ").x
            origin_x = imgui.get_cursor_pos_x()
            for key, label in rows:
                imgui.text_colored(GUI_TEXT, label)
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
            end_fields()

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
            begin_fields(f"##fields-btop-{title}")
            label_width = max(imgui.calc_text_size(label).x for _key, label in rows)
            gap = imgui.calc_text_size("    ").x
            origin_x = imgui.get_cursor_pos_x()
            for key, label in rows:
                imgui.text_colored(GUI_TEXT, label)
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
            end_fields()

        for title, fields in BTOP_GROUPS:
            draw_btop_group(title, fields)

def launcher_config_path():
    return Path.home() / ".config/bspwm/rices" / get_current_theme() / "config" / "rofi"


def read_rofi_option(key, default, allowed):
    path = launcher_config_path()
    if path.is_file():
        for line in path.read_text().splitlines():
            if line.startswith(f"{key}="):
                value = line.split("=", 1)[1].strip()
                if value in allowed:
                    return value
    return default


def write_rofi_option(key, value):
    path = launcher_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    current = {}
    if path.is_file():
        for line in path.read_text().splitlines():
            if "=" not in line:
                continue
            name, stored = line.split("=", 1)
            current[name.strip()] = stored.strip()
    current[key] = value
    lines = []
    for name in ("launcher", "icons"):
        if name in current:
            lines.append(f"{name}={current[name]}")
    path.write_text("\n".join(lines) + "\n")


def read_launcher():
    return read_rofi_option("launcher", "drun2", ("drun", "drun2"))


def write_launcher(name):
    write_rofi_option("launcher", name)


def launcher_panel():
    title = "Launcher"
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.push_font(None, imgui.get_style().font_size_base * 1.4)
    imgui.text_colored(GUI_ACCENT, title)
    imgui.pop_font()

    imgui.new_line()
    begin_fields("##fields-launcher")
    current = read_launcher()
    for name, label in (("drun", "Drun"), ("drun2", "Drun 2")):
        if imgui.radio_button(label, current == name):
            write_launcher(name)

    imgui.text_colored(GUI_TEXT, "Icons:")
    icons = read_rofi_option("icons", "no", ("yes", "no"))
    for value, label in (("yes", "Yes"), ("no", "No")):
        imgui.same_line()
        if imgui.radio_button(f"{label}##icons", icons == value):
            write_rofi_option("icons", value)
    end_fields()

def biblia_panel():
    title = "Linux biblia"
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.push_font(None, imgui.get_style().font_size_base * 1.4)
    imgui.text_colored(GUI_ACCENT, title)
    imgui.pop_font()


    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "Directories Found on Linux Systems")
    imgui.pop_font()

    imgui.new_line()

    rows = [
        ("/etc", "the /etc directory contains all the system-wide configuration files."),
        ("/home", 'in normal configurations, each user is given a directory in /home. ordinary users can write files only in their home directories'),
        ("/lib", "contains shared library files used by the core system programs"),
        ("/lost+found", "each formatted partition or device using a linux file system, such as ext3, will have this directory. it is used in the case of a partial recovery from a file system corruption event."),
        ("/media", "on older linux systems, the /mnt directory contains mount points for removable devices that have been mounted manually"),
        ("/opt", "the /opt directory is used to install “optional” software."),
        ("/proc", "the /proc directory is special. it’s not a real file system in the sense of files stored on your hard drive."),
        ("/root", "this is the home directory for the root account."),
        ("/sbin", "this directory contains “system” binaries."),
        ("/tmp", "the /tmp directory is intended for the storage of temporary, transient files created by various programs."),
        ("/usr", "the /usr directory tree is likely the largest one on a linux system."),
        ("/usr/bin", "/usr/bin contains the executable programs installed by your linux distribution."),
        ("/usr/lib", "the shared libraries for the programs in /usr/bin."),
        ("/usr/local", "the /usr/local tree is where programs that are not included with your distribution but are intended for system-wide use are installed."),
        ("/usr/sbin", "contains more system administration programs."),
        ("/usr/share", "/usr/share contains all the shared data used by programs in /usr/bin."),
        ("usr/share/doc", "most packages installed on the system will include some kind of documentation."),
        ("/var", "with the exception of /tmp and /home, the directories we have looked at so far remain relatively static; that is, their contents don’t change."),
        ("/var/log", "var/log contains log files, records of various system activity."),
    ]
    begin_fields("##fields-biblia")
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    value_x = imgui.get_cursor_pos_x() + label_width + gap

    def wrapped(text, x, width):
        line = ""
        first = True
        for word in text.split():
            trial = word if not line else f"{line} {word}"
            if imgui.calc_text_size(trial).x <= width:
                line = trial
                continue
            if line:
                if not first:
                    imgui.set_cursor_pos_x(x)
                imgui.text(line)
                first = False
            line = word
        if not line:
            return
        if not first:
            imgui.set_cursor_pos_x(x)
        imgui.text(line)

    for label, value in rows:
        imgui.text_colored(GUI_TEXT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(value_x)
        wrapped(value, value_x, max(40.0, imgui.get_content_region_avail().x))
    end_fields()

    imgui.new_line()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "Permissions")
    imgui.pop_font()

    imgui.new_line()
    rows = [
        ("-rwxrw-r--", "1 type, 2 owner, 3 group, 4 others."),
        ("-", "Regular file."),
        ("d", "Directory."),
        ("l", "Symlink. Rights are on the target."),
        ("c", "Character device. Byte stream."),
        ("b", "Block device. Data in blocks."),
        ("r file", "Read the file."),
        ("r dir", "List names. Needs x."),
        ("w file", "Write or truncate. Not rename or delete."),
        ("w dir", "Create, delete, rename inside. Needs x."),
        ("x file", "Run. Scripts also need r."),
        ("x dir", "Enter with cd."),
        ("chmod", "Changes the mode. One digit each: owner, group, others."),
        ("umask", "Bits taken off new files. 022 gives files 644, dirs 755."),
    ]
    begin_fields("##fields-permission")
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    value_x = imgui.get_cursor_pos_x() + label_width + gap

    for label, value in rows:
        imgui.text_colored(GUI_TEXT, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(value_x)
        wrapped(value, value_x, max(40.0, imgui.get_content_region_avail().x))
    end_fields()

    imgui.new_line()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "chmod")
    imgui.pop_font()

    imgui.new_line()

    modes = (
        ("0", "000", "---"),
        ("1", "001", "--x"),
        ("2", "010", "-w-"),
        ("3", "011", "-wx"),
        ("4", "100", "r--"),
        ("5", "101", "r-x"),
        ("6", "110", "rw-"),
        ("7", "111", "rwx"),
    )
    begin_fields("##fields-chmod")
    gap = imgui.calc_text_size("    ").x
    origin = imgui.get_cursor_pos_x()
    bin_x = origin + imgui.calc_text_size("octal").x + gap
    mode_x = bin_x + imgui.calc_text_size("binary").x + gap
    imgui.text_colored(GUI_TEXT, "chmod 754 file")
    imgui.same_line()
    imgui.set_cursor_pos_x(mode_x)
    imgui.text("owner, group, others")
    for title, x in (("octal", origin), ("binary", bin_x), ("mode", mode_x)):
        if x != origin:
            imgui.same_line()
            imgui.set_cursor_pos_x(x)
        imgui.text(title)
    for octal, binary, mode in modes:
        imgui.text_colored(GUI_TEXT, octal)
        imgui.same_line()
        imgui.set_cursor_pos_x(bin_x)
        imgui.text(binary)
        imgui.same_line()
        imgui.set_cursor_pos_x(mode_x)
        imgui.text(mode)
    end_fields()

    imgui.new_line()


def autostart_panel():
    title = "Autostart"
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.push_font(None, imgui.get_style().font_size_base * 1.4)
    imgui.text_colored(GUI_ACCENT, title)
    imgui.pop_font()
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
    begin_fields("##fields-autostart-add")
    imgui.text_colored(GUI_TEXT, "App:")
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

    imgui.text_colored(GUI_TEXT, "Link:")
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
        imgui.text_colored(GUI_TEXT, "Window:")
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
    end_fields()

    imgui.new_line()
    for index, entry in enumerate(list(entries)):
        begin_fields(f"##fields-autostart-{index}")
        title = entry["url"] or entry.get("title") or entry["class"] or entry["exec"]
        imgui.text_colored(GUI_TEXT, title)
        if entry["exec"] and not entry["url"]:
            imgui.same_line()
            imgui.text_colored(GUI_TEXT, entry["exec"])
        imgui.same_line()
        if imgui.button(f"Remove##autostart-{index}"):
            entries.pop(index)
            save_autostart()
            end_fields()
            continue
        imgui.text_colored(GUI_TEXT, "Desktop:")
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
                imgui.text_colored(GUI_TEXT, f"{label}:")
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
        end_fields()


PAGES = (
    ("Control Panel", icons.ICON_FA_SLIDERS_H, control_panel),
    ("Appearance", icons.ICON_FA_PAINT_BRUSH, appearance_panel),
    ("Launcher", icons.ICON_FA_ROCKET, launcher_panel),
    ("Autostart", icons.ICON_FA_BOLT, autostart_panel),
    ("Cheatsheet", icons.ICON_FA_BOOK, cheatsheet_panel),
    ("Biblia", icons.ICON_FA_BIBLE, biblia_panel),
)
SIDEBAR_WIDTH = 196


def nav_item(label, icon, selected):
    width = imgui.get_content_region_avail().x
    height = 40
    pos = imgui.get_cursor_screen_pos()
    clicked = imgui.invisible_button(f"##nav-{label}", imgui.ImVec2(width, height))
    hovered = imgui.is_item_hovered()
    if hovered:
        imgui.set_mouse_cursor(imgui.MouseCursor_.hand)

    if selected:
        fill = GUI_ACCENT
        text = GUI_BG
    elif hovered:
        fill = GUI_BUTTON_HOVERED
        text = GUI_TEXT
    else:
        fill = None
        text = GUI_TEXT

    draw = imgui.get_window_draw_list()
    rect_min = imgui.ImVec2(pos.x + 8, pos.y + 3)
    rect_max = imgui.ImVec2(pos.x + width - 8, pos.y + height - 3)
    if fill is not None:
        draw.add_rect_filled(rect_min, rect_max, imgui.color_convert_float4_to_u32(fill), 12)

    caption = f"{icon}   {label}"
    text_size = imgui.calc_text_size(caption)
    draw.add_text(
        imgui.ImVec2(rect_min.x + 12, pos.y + (height - text_size.y) * 0.5),
        imgui.color_convert_float4_to_u32(text),
        caption,
    )
    return clicked


def show_sidebar():
    imgui.push_style_var(imgui.StyleVar_.item_spacing, imgui.ImVec2(0, 2))
    imgui.push_style_var(imgui.StyleVar_.window_padding, imgui.ImVec2(0, 12))
    imgui.begin_child(
        "##nav",
        imgui.ImVec2(SIDEBAR_WIDTH, 0),
        imgui.ChildFlags_.always_use_window_padding,
    )
    for index, (label, icon, _draw) in enumerate(PAGES):
        if nav_item(label, icon, show_sidebar.page == index):
            show_sidebar.page = index
    imgui.end_child()
    imgui.pop_style_var(2)

    imgui.same_line(0, 0)
    imgui.push_style_var(imgui.StyleVar_.window_padding, imgui.ImVec2(16, 12))
    imgui.begin_child("##page", imgui.ImVec2(0, 0), imgui.ChildFlags_.always_use_window_padding)
    PAGES[show_sidebar.page][2]()
    imgui.end_child()
    imgui.pop_style_var()


show_sidebar.page = 0


def main():

    params = hello_imgui.RunnerParams()

    params.app_window_params.window_title = "Arch Control Panel"

    params.app_window_params.window_geometry.size = (1080, 680)

    params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_window
    )

    params.ini_disable = True
    params.ini_clear_previous_settings = True
    params.imgui_window_params.background_color = BACKGROUND
    params.callbacks.default_icon_font = hello_imgui.DefaultIconFont.font_awesome6
    params.callbacks.setup_imgui_style = setup_style

    def show_gui():
        if reload_panel_if_theme_changed():
            forget_live_configs()
            setup_style()
            params.imgui_window_params.background_color = GUI_BG
        show_sidebar()

    params.callbacks.show_gui = show_gui

    hello_imgui.run(params)


if __name__ == "__main__":
    main()
