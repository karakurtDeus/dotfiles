#!/usr/bin/env python3

import ctypes
import signal
import time

x11 = ctypes.CDLL("libX11.so.6")
fixes = ctypes.CDLL("libXfixes.so.3")

x11.XOpenDisplay.restype = ctypes.c_void_p
x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
x11.XDefaultRootWindow.restype = ctypes.c_ulong
x11.XFlush.argtypes = [ctypes.c_void_p]
x11.XQueryPointer.argtypes = [
    ctypes.c_void_p,
    ctypes.c_ulong,
    ctypes.POINTER(ctypes.c_ulong),
    ctypes.POINTER(ctypes.c_ulong),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_uint),
]
x11.XQueryPointer.restype = ctypes.c_int
fixes.XFixesHideCursor.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
fixes.XFixesShowCursor.argtypes = [ctypes.c_void_p, ctypes.c_ulong]

display = x11.XOpenDisplay(None)
if not display:
    raise SystemExit(0)
root = x11.XDefaultRootWindow(display)
stop = False


def request_stop(*_args):
    global stop
    stop = True


def pointer():
    root_return = ctypes.c_ulong()
    child_return = ctypes.c_ulong()
    root_x = ctypes.c_int()
    root_y = ctypes.c_int()
    win_x = ctypes.c_int()
    win_y = ctypes.c_int()
    mask = ctypes.c_uint()
    x11.XQueryPointer(
        display,
        root,
        ctypes.byref(root_return),
        ctypes.byref(child_return),
        ctypes.byref(root_x),
        ctypes.byref(root_y),
        ctypes.byref(win_x),
        ctypes.byref(win_y),
        ctypes.byref(mask),
    )
    return root_x.value, root_y.value


signal.signal(signal.SIGTERM, request_stop)
signal.signal(signal.SIGINT, request_stop)
origin = pointer()
fixes.XFixesHideCursor(display, root)
x11.XFlush(display)
while not stop and pointer() == origin:
    time.sleep(0.03)
fixes.XFixesShowCursor(display, root)
x11.XFlush(display)
