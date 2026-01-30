import os
import sys

# Fix for --windows-disable-console: redirect stdout/stderr to devnull
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import tkinter as tk

from speed import ProxySpeedTester


def main():
    root = tk.Tk()
    ProxySpeedTester(root)
    root.mainloop()


if __name__ == "__main__":
    main()
