import os
import sys

# Fix for --windows-disable-console: redirect stdout/stderr to devnull
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import tkinter as tk

from speed import ProxySpeedTester

_ICON_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAqElEQVR42t2XMRLAIAgE"
    "+UCKVPlaXphvms5KEfBOTJyxze5k4ASRxjnOqzCuaIcFNckgPng/Rb2qBBPcg08LWMAa"
    "vAqwwCN4lWCArXCTgBfsgasCEbAX3hSIgiNwqEA4kJB/IJQF2wmsbkthg4dpyARbilNY"
    "4OkoZhXdki74dhIyXz54DUBmw0gHQIdTTxtSpmNPCKUK0PaDdIGMrQi6mPxDIH05zVzP"
    "X9WLnasSwd3OAAAAAElFTkSuQmCC"
)


def main():
    root = tk.Tk()

    # Set window icon from embedded PNG (works in both dev and compiled)
    try:
        photo = tk.PhotoImage(data=_ICON_B64)
        root.iconphoto(True, photo)
        root._icon = photo  # prevent garbage collection
    except Exception:
        pass

    # Also set .ico for better Windows taskbar quality (dev mode)
    try:
        ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        if os.path.exists(ico):
            root.iconbitmap(ico)
    except Exception:
        pass

    ProxySpeedTester(root)
    root.mainloop()


if __name__ == "__main__":
    main()
