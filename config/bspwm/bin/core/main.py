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

def colors_panel():
    title = "Colors"

    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.push_font(None, imgui.get_style().font_size_base * 1.4)
    imgui.text_colored(GUI_ACCENT, title)
    imgui.pop_font()

    imgui.push_font(None, imgui.get_style().font_size_base * 1.2)
    imgui.text_colored(GUI_ACCENT, "BSPWM")
    imgui.pop_font()

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
        ("Colors", colors_panel),
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