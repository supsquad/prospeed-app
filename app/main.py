import tkinter as tk

from .speed import ProxySpeedTester


def main():
    root = tk.Tk()
    ProxySpeedTester(root)
    root.mainloop()


if __name__ == "__main__":
    main()
