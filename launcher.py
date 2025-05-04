import tkinter as tk
from core.auth import AuthWindow

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthWindow(root)
    root.mainloop()
