import tkinter as tk
from tkinter import messagebox, font
import random
import time
from PIL import Image, ImageTk  # You'll need to pip install pillow
import os

# Import after successful authentication
# from main import CypherApp

# Configuration - matched with main app styling
BG_COLOR = "#0D1117"  # Darker background for modern hacker feel
FG_COLOR = "#4AFF91"  # Brighter green for better contrast
ACCENT_COLOR = "#00CFFF"  # Bright cyan for highlights
HEADER_BG = "#161B22"  # Slightly lighter than bg for header distinction
ERROR_COLOR = "#FF3333"  # Red for errors

# Replace with your actual password
MASTER_PASSWORD = "cypher123"  # This should be in a secure config file


class AuthWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("CYPHER")
        self.root.configure(bg=BG_COLOR)

        # Center the window and set size
        window_width = 500
        window_height = 360  # Increased height to accommodate the checkbox
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

        # Make window non-resizable
        self.root.resizable(False, False)

        # Create title bar
        self.title_bar = tk.Frame(root, bg=HEADER_BG, height=40)
        self.title_bar.pack(fill=tk.X)

        # CYPHER logo/title
        self.title_label = tk.Label(
            self.title_bar,
            text="CYPHER",
            fg=ACCENT_COLOR,
            bg=HEADER_BG,
            font=("Orbitron", 16, "bold")  # Use Orbitron font if available
        )
        self.title_label.pack(side=tk.LEFT, padx=15, pady=5)

        # Version label
        self.version_label = tk.Label(
            self.title_bar,
            text="SECURITY",
            fg=FG_COLOR,
            bg=HEADER_BG,
            font=("Courier", 10)
        )
        self.version_label.pack(side=tk.LEFT, padx=5, pady=5)

        # Exit button
        self.exit_button = tk.Button(
            self.title_bar,
            text="×",
            fg=FG_COLOR,
            bg=HEADER_BG,
            font=("Arial", 16, "bold"),
            relief=tk.FLAT,
            command=self.root.destroy,
            activebackground=ERROR_COLOR,
            activeforeground="#FFFFFF",
            bd=0,
            padx=10
        )
        self.exit_button.pack(side=tk.RIGHT)

        # Main content frame
        self.content_frame = tk.Frame(root, bg=BG_COLOR)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create ASCII art for CYPHER
        self.ascii_art = tk.Label(
            self.content_frame,
            text=self.get_cypher_ascii(),
            fg=ACCENT_COLOR,
            bg=BG_COLOR,
            font=("Courier", 10),
            justify=tk.LEFT
        )
        self.ascii_art.pack(pady=(10, 20))

        # Access message with border
        self.message_frame = tk.Frame(self.content_frame, bg=HEADER_BG, bd=1, relief=tk.SUNKEN)
        self.message_frame.pack(fill=tk.X, pady=10)

        self.message_label = tk.Label(
            self.message_frame,
            text="TERMINAL ACCESS RESTRICTED",
            fg=FG_COLOR,
            bg=HEADER_BG,
            font=("Courier", 12, "bold"),
            padx=10,
            pady=8
        )
        self.message_label.pack()

        # Entry frame
        self.entry_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        self.entry_frame.pack(pady=20)

        # Access key label
        self.label = tk.Label(
            self.entry_frame,
            text="Enter Access Key:",
            fg=FG_COLOR,
            bg=BG_COLOR,
            font=("Courier", 12)
        )
        self.label.pack(pady=(0, 10))

        # Password entry with custom styling
        self.entry = tk.Entry(
            self.entry_frame,
            show="•",
            width=25,
            font=("Courier", 14),
            bg="#161B22",
            fg=FG_COLOR,
            insertbackground=ACCENT_COLOR,
            relief=tk.FLAT,
            bd=0
        )
        self.entry.pack(pady=(0, 5))
        self.entry.focus()

        # Create a line below the entry for better visual appearance
        self.entry_line = tk.Frame(self.entry_frame, height=2, bg=ACCENT_COLOR)
        self.entry_line.pack(fill=tk.X)

        # Add show/hide password checkbox
        self.show_password_var = tk.BooleanVar()
        self.show_password_var.set(False)

        self.show_password_check = tk.Checkbutton(
            self.entry_frame,
            text="Show Password",
            variable=self.show_password_var,
            onvalue=True,
            offvalue=False,
            command=self.toggle_password_visibility,
            fg=FG_COLOR,
            bg=BG_COLOR,
            selectcolor=HEADER_BG,
            activebackground=BG_COLOR,
            activeforeground=ACCENT_COLOR,
            font=("Courier", 10)
        )
        self.show_password_check.pack(pady=(5, 5))

        # Login button
        self.login_button = tk.Button(
            self.entry_frame,
            text="ACCESS TERMINAL",
            fg=BG_COLOR,
            bg=ACCENT_COLOR,
            font=("Courier", 12, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.verify_password,
            activebackground=FG_COLOR,
            activeforeground=BG_COLOR,
            cursor="hand2"
        )
        self.login_button.pack(pady=20)

        # Status message at bottom
        self.status_label = tk.Label(
            self.content_frame,
            text="SYSTEM READY",
            fg=FG_COLOR,
            bg=BG_COLOR,
            font=("Courier", 10)
        )
        self.status_label.pack(side=tk.BOTTOM, pady=5)

        # Bind events
        self.entry.bind("<Return>", self.verify_password)
        self.login_button.bind("<Enter>", lambda e: self.login_button.config(bg=FG_COLOR))
        self.login_button.bind("<Leave>", lambda e: self.login_button.config(bg=ACCENT_COLOR))

    def toggle_password_visibility(self):
        """Toggle the visibility of the password field"""
        if self.show_password_var.get():
            self.entry.config(show="")  # Show text
        else:
            self.entry.config(show="•")  # Hide text (show bullets)

    def get_cypher_ascii(self):
        """Return ASCII art for CYPHER"""
        return (
            " ██████╗██╗   ██╗██████╗ ██╗  ██╗███████╗██████╗ \n"
            "██╔════╝╚██╗ ██╔╝██╔══██╗██║  ██║██╔════╝██╔══██╗\n"
            "██║      ╚████╔╝ ██████╔╝███████║█████╗  ██████╔╝\n"
            "██║       ╚██╔╝  ██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗\n"
            "╚██████╗   ██║   ██║     ██║  ██║███████╗██║  ██║\n"
            " ╚═════╝   ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"
        )

    def verify_password(self, event=None):
        """Verify the entered password"""
        password = self.entry.get()

        # Update status
        self.status_label.config(text="VERIFYING...", fg=ACCENT_COLOR)
        self.root.update()
        time.sleep(0.5)  # Add slight delay for effect

        if password == MASTER_PASSWORD:
            self.status_label.config(text="ACCESS GRANTED", fg=FG_COLOR)
            self.successful_login_animation()
        else:
            self.entry.delete(0, tk.END)
            self.status_label.config(text="ACCESS DENIED", fg=ERROR_COLOR)
            self.failed_login_animation()

    def successful_login_animation(self):
        """Animation for successful login"""
        # Blink the status message
        for _ in range(3):
            self.status_label.config(fg=BG_COLOR)
            self.root.update()
            time.sleep(0.1)
            self.status_label.config(fg=FG_COLOR)
            self.root.update()
            time.sleep(0.1)

        # Show success message
        self.label.config(text="ACCESS GRANTED", fg=FG_COLOR)
        self.entry.config(state=tk.DISABLED)
        self.login_button.config(state=tk.DISABLED)

        # Display loading message
        self.status_label.config(text="LAUNCHING TERMINAL...", fg=ACCENT_COLOR)
        self.root.update()

        # Delay for effect
        time.sleep(1)

        # Destroy current window and open main application
        self.root.destroy()

        # Create main application window
        terminal = tk.Tk()

        # This import is done here to prevent circular imports
        from main import CypherApp
        CypherApp(terminal)
        terminal.mainloop()

    def failed_login_animation(self):
        """Animation for failed login"""
        # Shake the window
        x = self.root.winfo_x()
        y = self.root.winfo_y()

        # Flash the entry with red color
        original_bg = self.entry.cget("bg")
        self.entry.config(bg=ERROR_COLOR)
        self.root.update()

        # Shake effect
        for _ in range(5):
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-5, 5)
            self.root.geometry(f"+{x + offset_x}+{y + offset_y}")
            self.root.update()
            time.sleep(0.05)

        # Reset window position
        self.root.geometry(f"+{x}+{y}")

        # Reset entry background
        self.entry.config(bg=original_bg)

        # Glitch text effect for message
        self.label.config(text=self.glitch_text("ACCESS DENIED"), fg=ERROR_COLOR)
        self.root.update()
        time.sleep(1)
        self.label.config(text="Enter Access Key:", fg=FG_COLOR)

    def glitch_text(self, base_text):
        """Create a glitched text effect"""
        chars = list("█▓▒░ ")
        glitch = ""
        for _ in range(3):
            glitch += random.choice(chars)
        return glitch + " " + base_text + " " + glitch


if __name__ == "__main__":
    root = tk.Tk()
    app = AuthWindow(root)
    root.mainloop()