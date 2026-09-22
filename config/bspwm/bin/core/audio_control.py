import ctypes
import re
import subprocess


def _ui_max_percent():
    # PulseAudio UI ceiling: +11 dB above normal, shown by pactl as a percent.
    lib = ctypes.CDLL("libpulse.so.0")
    lib.pa_sw_volume_from_dB.restype = ctypes.c_uint32
    lib.pa_sw_volume_from_dB.argtypes = [ctypes.c_double]
    raw = lib.pa_sw_volume_from_dB(11.0)
    return round(raw * 100 / 0x10000)


VOLUME_MAX = _ui_max_percent()


def max_volume():
    return VOLUME_MAX


def get_volume():
    text = subprocess.check_output(
        ["pactl", "get-sink-volume", "@DEFAULT_SINK@"], text=True
    )
    match = re.search(r"(\d+)%", text)
    if not match:
        return 0
    return int(match.group(1))


def set_volume(percent):
    percent = max(0, min(int(percent), VOLUME_MAX))
    subprocess.run(
        ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percent}%"],
        check=True,
    )


def _muted(kind):
    text = subprocess.check_output(
        ["pactl", f"get-{kind}-mute", f"@DEFAULT_{kind.upper()}@"], text=True
    )
    return "yes" in text.lower()


def _set_muted(kind, muted):
    subprocess.run(
        ["pactl", f"set-{kind}-mute", f"@DEFAULT_{kind.upper()}@", "1" if muted else "0"],
        check=True,
    )


def is_audio_muted():
    return _muted("sink")


def set_audio_muted(muted):
    _set_muted("sink", muted)


def is_mic_muted():
    return _muted("source")


def set_mic_muted(muted):
    _set_muted("source", muted)
