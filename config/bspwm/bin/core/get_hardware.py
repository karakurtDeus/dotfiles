from pathlib import Path
import os
import pwd
import subprocess


def cpu_name():
    for line in Path("/proc/cpuinfo").read_text().splitlines():
        if line.startswith("model name"):
            return line.split(":", 1)[1].strip()


def gpu_names():
    out = subprocess.check_output(["lspci", "-mm"], text=True)
    names = []

    for line in out.splitlines():
        fields = [part.strip('"') for part in line.split('"')[1::2]]
        if not fields:
            continue
        if "VGA" in fields[0] or "3D" in fields[0] or "Display" in fields[0]:
            device = fields[2]
            start = device.find("[")
            end = device.rfind("]")
            if start != -1 and end > start:
                device = device[start + 1:end]
            names.append(device)

    if not names:
        return "No GPU found"

    return ", ".join(names)



def kernel_version():
    return Path("/proc/sys/kernel/osrelease").read_text().strip()


def package_count():
    # pacman -Q includes repo packages and foreign ones installed with yay
    out = subprocess.check_output(["pacman", "-Qq"], text=True)
    return sum(1 for line in out.splitlines() if line.strip())