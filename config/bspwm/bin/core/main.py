
from imgui_bundle import imgui, hello_imgui
import getpass

from colors import color_to_hex, hex_to_color
from terminal import get_terminal_settings, set_background

# Get the username
username = getpass.getuser()

# Initial color, same hex format as kitty.conf
color_terminal = get_terminal_settings()
if color_terminal is None:
    color_terminal = "#6699FF"

alert_color = None
if alert_color is None:
    alert_color = "#6699FF"

picker_color = hex_to_color(color_terminal)
alert_color = hex_to_color(alert_color)

# --------------------------
# Control Panel
# --------------------------

def control_panel():
    global picker_color, alert_color
    title = "Control Panel"

    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.text(title)

    imgui.separator()

    imgui.text("Select alert color:")

    _, alert_color = imgui.color_edit3("Color", alert_color)

    if imgui.button("Apply"):
        color_terminal = color_to_hex(alert_color)
        pass



# --------------------------
# terminal
# --------------------------

def terminal():

    global color_terminal, picker_color

    title = "Terminal Settings"
    # Center the title
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.text(title)

    imgui.separator()


    # Color edit
    imgui.text("Background color:")

    _, picker_color = imgui.color_edit3("Color", picker_color)

    if imgui.button("Apply"):
        color_terminal = color_to_hex(picker_color)
        set_background(color_terminal)


# --------------------------
# Application
# --------------------------

def main():

    params = hello_imgui.RunnerParams()

    params.app_window_params.window_title = "Arch Control Panel"

    params.app_window_params.window_geometry.size = (900, 600)

    # Enable docking
    params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )

    # Clear the saved layout
    params.ini_clear_previous_settings = True

    # Main GUI
    params.callbacks.show_gui = lambda: None

    # Window list
    windows = [
        ("Control Panel", control_panel),
        ("Terminal", terminal),
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