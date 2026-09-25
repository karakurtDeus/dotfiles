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
    for color in SURFACES:
        style.set_color_(color, BACKGROUND)
    style.set_color_(imgui.Col_.text, GUI_TEXT)
    style.set_color_(imgui.Col_.text_link, GUI_TEXT)
    style.set_color_(imgui.Col_.button, GUI_BUTTON)
    style.set_color_(imgui.Col_.button_hovered, GUI_BUTTON_HOVERED)
    style.set_color_(imgui.Col_.button_active, GUI_BUTTON_ACTIVE)
    style.set_color_(imgui.Col_.tab, GUI_TAB)
    style.set_color_(imgui.Col_.tab_hovered, GUI_TAB_HOVERED)
    style.set_color_(imgui.Col_.tab_selected, GUI_TAB_SELECTED)
    style.set_color_(imgui.Col_.tab_dimmed, GUI_TAB)
    style.set_color_(imgui.Col_.tab_dimmed_selected, GUI_TAB_SELECTED)


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
    params.imgui_window_params.background_color = BACKGROUND
    params.callbacks.setup_imgui_style = setup_style

    # Main GUI
    params.callbacks.show_gui = lambda: None

    # Window list
    windows = [
        ("Control Panel", control_panel),
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