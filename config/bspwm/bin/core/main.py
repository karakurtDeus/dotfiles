
from imgui_bundle import imgui, hello_imgui
import getpass
import time
from get_hardware import cpu_name, gpu_names, kernel_version, package_count
from colors import (
    color_to_hex,
    hex_to_color,
    load_polybar_colors,
    restart_polybar,
    save_polybar_colors,
)
from dunst import load_dunst_colors, reload_dunst, save_dunst_colors
from lockscreen import load_lockscreen_colors, save_lockscreen_colors
from rofi_colors import load_rofi_colors, save_rofi_colors
from terminal import get_terminal_settings, set_background
from audio_control import (
    get_volume,
    is_audio_muted,
    is_mic_muted,
    max_volume,
    set_audio_muted,
    set_mic_muted,
    set_volume,
)

# Get the username
username = getpass.getuser()
cpu_name = cpu_name()
gpu_names = gpu_names()
kernel_version = kernel_version()
package_count = package_count()

# Initial color, same hex format as kitty.conf
color_terminal = get_terminal_settings()
if color_terminal is None:
    color_terminal = "#6699FF"

picker_color = hex_to_color(color_terminal)
polybar_entries = load_polybar_colors()
polybar_pickers = {name: hex_to_color(value) for name, value in polybar_entries}
dunst_background, dunst_alerts = load_dunst_colors()
dunst_background_color = hex_to_color(dunst_background or "#000000")
dunst_pickers = {name: hex_to_color(value) for name, value in dunst_alerts}
lockscreen_colors = load_lockscreen_colors()
lockscreen_pickers = {name: hex_to_color(rgb) for name, rgb, _alpha in lockscreen_colors}
rofi_colors = load_rofi_colors()
rofi_pickers = {name: hex_to_color(value) for name, value in rofi_colors}
volume_max = max_volume()
volume = get_volume()
audio_muted = is_audio_muted()
mic_muted = is_mic_muted()
volume_stamp = time.monotonic()

# --------------------------
# Control Panel
# --------------------------

def control_panel():
    global picker_color, alert_color, volume, audio_muted, mic_muted, volume_stamp
    title = f"Welcome, {username}!"

    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.text(title)

    imgui.separator()

    accent = imgui.get_style_color_vec4(imgui.Col_.text_link)

    rows = [
        ("Kernel:", kernel_version),
        ("Packages:", package_count),
        ("CPU:", cpu_name),
        ("GPU:", gpu_names),
    ]
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(accent, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text(str(value))

    imgui.separator()

    # AUDIO 
    title = "Audio Settings"
    # Center the title
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.text(title)

    now = time.monotonic()
    if now - volume_stamp > 0.5:
        volume = get_volume()
        audio_muted = is_audio_muted()
        mic_muted = is_mic_muted()
        volume_stamp = now

    imgui.begin_group()
    changed, volume = imgui.v_slider_int(
        "##volume", imgui.ImVec2(36, 140), volume, 0, volume_max, "%d"
    )
    if changed:
        set_volume(volume)
        volume_stamp = time.monotonic()
    imgui.text("Master")
    imgui.end_group()

    changed, audio_muted = imgui.checkbox("Mute audio", audio_muted)
    if changed:
        set_audio_muted(audio_muted)
        volume_stamp = time.monotonic()

    changed, mic_muted = imgui.checkbox("Mute microphone", mic_muted)
    if changed:
        set_mic_muted(mic_muted)
        volume_stamp = time.monotonic()

    imgui.separator()

# --------------------------
# Colors
# --------------------------

def colors_panel():
    global color_terminal, picker_color, dunst_background_color

    title = "Colors Settings"
    
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.text(title)

    imgui.separator()


    # Color edit
    title = "Polybar"
    
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.text(title)

    if polybar_entries:
        accent = imgui.get_style_color_vec4(imgui.Col_.text_link)
        label_width = max(
            imgui.calc_text_size(f"{name}:").x for name, _value in polybar_entries
        )
        gap = imgui.calc_text_size("    ").x
        origin_x = imgui.get_cursor_pos_x()
        flags = (
            imgui.ColorEditFlags_.uint8
            | imgui.ColorEditFlags_.display_hex
            | imgui.ColorEditFlags_.no_label
        )

        for name, _value in polybar_entries:
            imgui.text_colored(accent, f"{name}:")
            imgui.same_line()
            imgui.set_cursor_pos_x(origin_x + label_width + gap)
            imgui.set_next_item_width(130)
            _changed, polybar_pickers[name] = imgui.color_edit3(
                f"##polybar-{name}", polybar_pickers[name], flags
            )

        if imgui.button("Apply"):
            save_polybar_colors(
                [
                    (name, color_to_hex(polybar_pickers[name]))
                    for name, _value in polybar_entries
                ]
            )
            restart_polybar()

    imgui.separator()

    
    title = "Terminal"
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.text(title)

    accent = imgui.get_style_color_vec4(imgui.Col_.text_link)
    label = "background:"
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()
    flags = (
        imgui.ColorEditFlags_.uint8
        | imgui.ColorEditFlags_.display_hex
        | imgui.ColorEditFlags_.no_label
    )
    imgui.text_colored(accent, label)
    imgui.same_line()
    imgui.set_cursor_pos_x(origin_x + imgui.calc_text_size(label).x + gap)
    imgui.set_next_item_width(130)
    _, picker_color = imgui.color_edit3("##terminal-background", picker_color, flags)

    if imgui.button("Apply##terminal"):
        color_terminal = color_to_hex(picker_color)
        set_background(color_terminal)

    imgui.separator()

    title = "Dunst"
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.text(title)

    dunst_rows = ["background", *[name for name, _value in dunst_alerts]]
    if dunst_rows:
        accent = imgui.get_style_color_vec4(imgui.Col_.text_link)
        label_width = max(imgui.calc_text_size(f"{label}:").x for label in dunst_rows)
        gap = imgui.calc_text_size("    ").x
        origin_x = imgui.get_cursor_pos_x()
        flags = (
            imgui.ColorEditFlags_.uint8
            | imgui.ColorEditFlags_.display_hex
            | imgui.ColorEditFlags_.no_label
        )

        for label in dunst_rows:
            imgui.text_colored(accent, f"{label}:")
            imgui.same_line()
            imgui.set_cursor_pos_x(origin_x + label_width + gap)
            imgui.set_next_item_width(130)
            if label == "background":
                _changed, dunst_background_color = imgui.color_edit3(
                    "##dunst-background", dunst_background_color, flags
                )
            else:
                _changed, dunst_pickers[label] = imgui.color_edit3(
                    f"##dunst-{label}", dunst_pickers[label], flags
                )

        if imgui.button("Apply##dunst"):
            save_dunst_colors(
                color_to_hex(dunst_background_color),
                [(name, color_to_hex(dunst_pickers[name])) for name, _value in dunst_alerts],
            )
            reload_dunst()

    imgui.separator()

    title = "Lockscreen"
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.text(title)

    if lockscreen_colors:
        accent = imgui.get_style_color_vec4(imgui.Col_.text_link)
        label_width = max(
            imgui.calc_text_size(f"{name}:").x for name, _rgb, _alpha in lockscreen_colors
        )
        gap = imgui.calc_text_size("    ").x
        origin_x = imgui.get_cursor_pos_x()
        flags = (
            imgui.ColorEditFlags_.uint8
            | imgui.ColorEditFlags_.display_hex
            | imgui.ColorEditFlags_.no_label
        )

        for name, _rgb, _alpha in lockscreen_colors:
            imgui.text_colored(accent, f"{name}:")
            imgui.same_line()
            imgui.set_cursor_pos_x(origin_x + label_width + gap)
            imgui.set_next_item_width(130)
            _changed, lockscreen_pickers[name] = imgui.color_edit3(
                f"##lockscreen-{name}", lockscreen_pickers[name], flags
            )

        if imgui.button("Apply##lockscreen"):
            save_lockscreen_colors(
                [
                    (name, color_to_hex(lockscreen_pickers[name]), alpha)
                    for name, _rgb, alpha in lockscreen_colors
                ]
            )

    imgui.separator()

    title = "Rofi"
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.text(title)

    if rofi_colors:
        accent = imgui.get_style_color_vec4(imgui.Col_.text_link)
        label_width = max(
            imgui.calc_text_size(f"{name}:").x for name, _value in rofi_colors
        )
        gap = imgui.calc_text_size("    ").x
        origin_x = imgui.get_cursor_pos_x()
        flags = (
            imgui.ColorEditFlags_.uint8
            | imgui.ColorEditFlags_.display_hex
            | imgui.ColorEditFlags_.no_label
        )

        for name, _value in rofi_colors:
            imgui.text_colored(accent, f"{name}:")
            imgui.same_line()
            imgui.set_cursor_pos_x(origin_x + label_width + gap)
            imgui.set_next_item_width(130)
            _changed, rofi_pickers[name] = imgui.color_edit3(
                f"##rofi-{name}", rofi_pickers[name], flags
            )

        if imgui.button("Apply##rofi"):
            save_rofi_colors(
                [(name, color_to_hex(rofi_pickers[name])) for name, _value in rofi_colors]
            )

    imgui.separator()

def cheatsheet_panel():
    global color_terminal, picker_color, dunst_background_color

    title = "Cheatsheet"
    
    avail = imgui.get_content_region_avail().x
    text_width = imgui.calc_text_size(title).x
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail - text_width) * 0.5)
    imgui.text(title)

    imgui.separator()

    accent = imgui.get_style_color_vec4(imgui.Col_.text_link)

    rows = [
        ("Network manager:", "nmtui"),
        ("Bluethooth:", "bluetui"),
        ("Audio:", "wpctl status && wpctl set-default <device>"),
    ]
    label_width = max(imgui.calc_text_size(label).x for label, _ in rows)
    gap = imgui.calc_text_size("    ").x
    origin_x = imgui.get_cursor_pos_x()

    for label, value in rows:
        imgui.text_colored(accent, label)
        imgui.same_line()
        imgui.set_cursor_pos_x(origin_x + label_width + gap)
        imgui.text(str(value))




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