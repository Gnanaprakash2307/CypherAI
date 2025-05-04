import tkinter as tk
from tkinter import font, scrolledtext, ttk
import time
import datetime
import threading
import os
import requests
import google.generativeai as genai
import random

# Config
APP_TITLE = "CYPHER"  # Changed to just CYPHER
FONT_SIZE = 12
BG_COLOR = "#0D1117"  # Darker background for modern hacker feel
FG_COLOR = "#4AFF91"  # Brighter green for better contrast
ACCENT_COLOR = "#00CFFF"  # Bright cyan for highlights
CURSOR_COLOR = "#FF3333"  # Brighter red cursor
HEADER_BG = "#161B22"  # Slightly lighter than bg for header distinction
GEMINI_API_KEY = "AIzaSyCQwmLtnOvE5i8MjdAAd0lYl51sPEC082k"  # Replace with actual key

# Weather API Config
WEATHER_API_KEY = "YOUR_WEATHER_API_KEY"  # Replace with your weather API key
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# News API Config
NEWS_API_KEY = "c039f0cbce564bd1914cd47b637440e9"
NEWS_API_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

# Log file
LOG_FILE = "cypher_log.txt"

session_memory = []


class LoadingIndicator:
    def __init__(self, text_area):
        self.text_area = text_area
        self.running = False
        self.animation_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.position = None
        self.thread = None

    def start(self):
        self.running = True
        self.position = self.text_area.index(tk.INSERT)
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()

    def _animate(self):
        i = 0
        while self.running:
            char = self.animation_chars[i]
            self.text_area.delete(self.position, f"{self.position}+1c")
            self.text_area.insert(self.position, char)
            self.text_area.see(self.position)
            time.sleep(0.1)
            i = (i + 1) % len(self.animation_chars)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(0.2)
        if self.position:
            self.text_area.delete(self.position, f"{self.position}+1c")


class CypherApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.configure(bg=BG_COLOR)
        self.root.attributes('-fullscreen', True)

        # Set icon
        try:
            self.root.iconbitmap("cypher_icon.ico")  # Create or add an icon file
        except:
            pass

        # Configure the main frame with gradient effect
        self.main_frame = tk.Frame(root, bg=BG_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Create a title bar with CYPHER prominently displayed
        self.title_bar = tk.Frame(self.main_frame, bg=HEADER_BG, height=40)
        self.title_bar.pack(fill=tk.X, pady=(0, 10))

        # CYPHER logo/text in title bar
        self.title_label = tk.Label(
            self.title_bar,
            text="CYPHER",
            fg=ACCENT_COLOR,
            bg=HEADER_BG,
            font=("Orbitron", 18, "bold")  # Use Orbitron font if available
        )
        self.title_label.pack(side=tk.LEFT, padx=15, pady=5)

        # Version label
        self.version_label = tk.Label(
            self.title_bar,
            text="v3.0",
            fg=FG_COLOR,
            bg=HEADER_BG,
            font=("Courier", 10)
        )
        self.version_label.pack(side=tk.LEFT, padx=5, pady=5)

        # Exit button in title bar
        self.exit_button = tk.Button(
            self.title_bar,
            text="×",
            fg=FG_COLOR,
            bg=HEADER_BG,
            font=("Arial", 18, "bold"),
            relief=tk.FLAT,
            command=self.quit_app,
            activebackground="#FF3333",
            activeforeground="#FFFFFF",
            bd=0,
            padx=10
        )
        self.exit_button.pack(side=tk.RIGHT)

        # Minimize button
        self.min_button = tk.Button(
            self.title_bar,
            text="−",
            fg=FG_COLOR,
            bg=HEADER_BG,
            font=("Arial", 18),
            relief=tk.FLAT,
            command=lambda: self.root.attributes('-fullscreen', False),
            activebackground=HEADER_BG,
            activeforeground=ACCENT_COLOR,
            bd=0,
            padx=10
        )
        self.min_button.pack(side=tk.RIGHT)

        # Header frame for clock and system info with border
        self.header_frame = tk.Frame(self.main_frame, bg=HEADER_BG, bd=1, relief=tk.RAISED)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))

        # System info display with icon
        self.sys_info = tk.Label(
            self.header_frame,
            text="● SYSTEM: OPERATIONAL",
            fg=ACCENT_COLOR,
            bg=HEADER_BG,
            font=("Courier", 10, "bold"),
            anchor="w",
            padx=10,
            pady=5
        )
        self.sys_info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Clock display with icon
        self.clock_display = tk.Label(
            self.header_frame,
            text="",
            fg=ACCENT_COLOR,
            bg=HEADER_BG,
            font=("Courier", 10, "bold"),
            padx=10,
            pady=5
        )
        self.clock_display.pack(side=tk.RIGHT)
        self.update_clock()

        try:
            self.custom_font = font.Font(family="Hack", size=FONT_SIZE)
        except:
            try:
                self.custom_font = font.Font(family="Consolas", size=FONT_SIZE)
            except:
                self.custom_font = font.Font(family="Courier", size=FONT_SIZE)

        # Terminal area with border styling
        self.text_frame = tk.Frame(self.main_frame, bg="#161B22", bd=1, relief=tk.SUNKEN)
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Custom scrollbar style
        style = ttk.Style()
        style.configure("Vertical.TScrollbar",
                        background=ACCENT_COLOR,
                        troughcolor=BG_COLOR,
                        arrowcolor=FG_COLOR)

        # Create a custom scrollbar
        self.scrollbar = ttk.Scrollbar(self.text_frame, style="Vertical.TScrollbar")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area = scrolledtext.ScrolledText(
            self.text_frame,
            bg=BG_COLOR,
            fg=FG_COLOR,
            insertbackground=CURSOR_COLOR,
            font=self.custom_font,
            borderwidth=0,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            selectbackground=ACCENT_COLOR,
            selectforeground="#000000",
            yscrollcommand=self.scrollbar.set
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.text_area.yview)

        # Command input area with a different look
        self.input_frame = tk.Frame(self.main_frame, bg=HEADER_BG, height=30, bd=1, relief=tk.RAISED)
        self.input_frame.pack(fill=tk.X, pady=(10, 5))

        self.cmd_prefix = tk.Label(
            self.input_frame,
            text=">",
            fg=ACCENT_COLOR,
            bg=HEADER_BG,
            font=self.custom_font,
            padx=5
        )
        self.cmd_prefix.pack(side=tk.LEFT)

        # Status bar with modern look
        self.status_bar = tk.Label(
            self.main_frame,
            text="STATUS: READY",
            fg=ACCENT_COLOR,
            bg=HEADER_BG,
            font=("Courier", 10, "bold"),
            anchor="w",
            padx=10,
            pady=3,
            bd=1,
            relief=tk.SUNKEN
        )
        self.status_bar.pack(fill=tk.X, pady=(5, 0))

        # Initialize loading indicator
        self.loading = LoadingIndicator(self.text_area)

        # Welcome message and daily greeting
        self.display_welcome()

        # Command history
        self.command_history = []
        self.history_index = -1

        # Configure Gemini AI
        genai.configure(api_key=GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")

        # Bind events
        self.text_area.bind("<Return>", self.process_command)
        self.text_area.bind("<Up>", self.navigate_history_up)
        self.text_area.bind("<Down>", self.navigate_history_down)
        self.root.bind('<Control-q>', self.quit_app)
        self.root.bind('<Control-Shift-D>', self.diagnostic_shortcut)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))

    def update_clock(self):
        """Update the clock display with current time"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock_display.config(text=f"⏰ TIME: {current_time}")
        self.root.after(1000, self.update_clock)  # Update every second

    def display_welcome(self):
        """Display welcome banner and daily greeting"""
        # More stylized ASCII art for CYPHER
        ascii_banner = (
            "  ██████╗██╗   ██╗██████╗ ██╗  ██╗███████╗██████╗ \n"
            " ██╔════╝╚██╗ ██╔╝██╔══██╗██║  ██║██╔════╝██╔══██╗\n"
            " ██║      ╚████╔╝ ██████╔╝███████║█████╗  ██████╔╝\n"
            " ██║       ╚██╔╝  ██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗\n"
            " ╚██████╗   ██║   ██║     ██║  ██║███████╗██║  ██║\n"
            "  ╚═════╝   ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝\n"
        )

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%A, %B %d, %Y")
        greeting = self.get_time_based_greeting()

        welcome_text = (
            f"\n{ascii_banner}\n"
            f"═══════════════════════════════════════════════════════\n"
            f">>> SYSTEM BOOT SEQUENCE COMPLETED\n"
            f">>> {current_date} | {current_time}\n"
            f">>> {greeting}, Operator\n"
            f">>> Type 'help' to view available commands\n"
            f"═══════════════════════════════════════════════════════\n\n> "
        )

        self.text_area.insert(tk.END, welcome_text)
        self.text_area.see(tk.END)

    def get_time_based_greeting(self):
        """Return appropriate greeting based on time of day"""
        hour = datetime.datetime.now().hour
        if hour < 12:
            return "Good morning Working Early Uhh"
        elif hour < 18:
            return "Good afternoon Get a nap man"
        else:
            return "Good evening Buckle up"

    def log_command(self, command):
        """Log command to file"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"[{timestamp}] {command}\n")

    def process_command(self, event):
        """Process the entered command"""
        # Get the current line and extract command
        self.text_area.mark_set("input_start", "insert linestart")
        input_text = self.text_area.get("input_start", "insert").strip()

        if input_text.startswith(">"):
            command = input_text[1:].strip()
            self.log_command(command)  # Log the command

            self.text_area.insert(tk.END, "\n")

            # Don't add empty commands to history
            if command:
                self.command_history.append(command)
                self.history_index = len(self.command_history)

            # Process the command
            self.handle_command(command)

        self.text_area.insert(tk.END, "\n> ")
        self.text_area.see(tk.END)
        return "break"  # Prevent default behavior

    def navigate_history_up(self, event):
        """Navigate command history upward"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.text_area.delete("input_start", "insert")
            self.text_area.insert("input_start", f"> {self.command_history[self.history_index]}")
        return "break"

    def navigate_history_down(self, event):
        """Navigate command history downward"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.text_area.delete("input_start", "insert")
            self.text_area.insert("input_start", f"> {self.command_history[self.history_index]}")
        else:
            # Clear the line when reaching end of history
            self.text_area.delete("input_start", "insert")
            self.text_area.insert("input_start", f"> ")
        return "break"

    def handle_command(self, command):
        """Handle different commands"""
        cmd = command.lower().strip()

        # Update status to processing and add visual indicator
        self.status_bar.config(text="STATUS: PROCESSING", fg="#FFCC00")
        self.status_bar.update()

        if not cmd:
            self.status_bar.config(text="STATUS: READY", fg=ACCENT_COLOR)
            return

        elif cmd == "help":
            response = (
                "╔════════════════════ AVAILABLE COMMANDS ════════════════════╗\n"
                "║ help         - Show available commands                     ║\n"
                "║ weather <city> - Show weather for specified city           ║\n"
                "║ news         - Show latest headlines                       ║\n"
                "║ ai <prompt>  - Ask Gemini AI a question                    ║\n"
                "║ ai --idea    - Get app ideas                               ║\n"
                "║ ai --code    - Get useful Python code                      ║\n"
                "║ ai --news    - Summarize today's tech news                 ║\n"
                "║ remember <text> - Store information in memory              ║\n"
                "║ what do i remember? - Show stored memory                   ║\n"
                "║ mission start/end - Toggle mission mode                    ║\n"
                "║ sys diagnostic - Run system diagnostics                    ║\n"
                "║ banner       - Show CYPHER banner                          ║\n"
                "║ clear        - Clear the terminal                          ║\n"
                "║ date         - Show current date and time                  ║\n"
                "║ log show     - Show command log                            ║\n"
                "║ self destruct - ???                                        ║\n"
                "║ quit / Ctrl+Q - Exit the application                       ║\n"
                "╚═══════════════════════════════════════════════════════════╝"
            )

        elif cmd.startswith("weather "):
            city = cmd.replace("weather ", "").strip()
            self.loading.start()
            response = self.fetch_weather(city)
            self.loading.stop()

        elif cmd == "news":
            self.loading.start()
            response = self.fetch_news()
            self.loading.stop()

        elif cmd.startswith("ai "):
            arg = cmd[3:].strip()
            self.loading.start()
            if arg == "--idea":
                response = self.ask_gemini("Give me an innovative app idea for students")
            elif arg == "--code":
                response = self.ask_gemini("Write a useful Python snippet with summary explanation")
            elif arg == "--news":
                response = self.ask_gemini("Summarize today's top 3 tech news")
            else:
                response = self.ask_gemini(arg)
            self.loading.stop()

        elif cmd.startswith("remember "):
            item = cmd.replace("remember ", "").strip()
            session_memory.append(item)
            response = f">>> 💾 Remembered: {item}"

        elif cmd == "what do i remember?":
            if session_memory:
                response = ">>> 🧠 Memory Dump:\n" + "\n".join(f"- {item}" for item in session_memory)
            else:
                response = ">>> 🧠 Memory Empty."

        elif cmd == "unlock secrets":
            response = ">>> 🔐 Access Granted: Cypher Core Ready."

        elif cmd == "mission start":
            response = ">>> 🎯 Mission Protocol Initiated. Focus Mode: ON."
            self.text_area.config(bg="#0A1015")  # Darker background for mission mode

        elif cmd == "mission end":
            response = ">>> ✅ Mission Completed. Returning to standard mode."
            self.text_area.config(bg=BG_COLOR)  # Return to normal background

        elif cmd == "sys diagnostic":
            response = self.run_diagnostics()

        elif cmd == "banner":
            response = (
                "██████╗░██╗░░░░░██████╗░██╗░░██╗███████╗██████╗░\n"
                "██╔══██╗██║░░░░░██╔══██╗██║░██╔╝██╔════╝██╔══██╗\n"
                "██████╔╝██║░░░░░██████╔╝█████═╝░█████╗░░██████╔╝\n"
                "██╔═══╝░██║░░░░░██╔═══╝░██╔═██╗░██╔══╝░░██╔═══╝░\n"
                "██║░░░░░███████╗██║░░░░░██║░╚██╗███████╗██║░░░░░"
            )

        elif cmd == "clear":
            self.text_area.delete(1.0, tk.END)
            response = ""  # No response needed, we'll add the prompt

        elif cmd == "date":
            now = datetime.datetime.now()
            response = f">>> Current Date and Time: {now.strftime('%A, %B %d, %Y at %H:%M:%S')}"

        elif cmd == "log show":
            response = self.read_log_file()

        elif cmd == "self destruct":
            response = self.simulate_self_destruct()

        elif cmd == "quit":
            self.quit_app()
            return

        else:
            response = f">>> Unknown command: {command}"

        # Display response with typewriter effect
        self.typewriter_effect(response)

        # Reset status to ready
        self.status_bar.config(text="STATUS: READY", fg=ACCENT_COLOR)

    def fetch_weather(self, city):
        """Fetch weather data for specified city"""
        try:
            params = {
                'q': city,
                'appid': WEATHER_API_KEY,
                'units': 'metric'
            }
            response = requests.get(WEATHER_API_URL, params=params)

            if response.status_code == 200:
                data = response.json()
                weather = data['weather'][0]['description']
                temp = data['main']['temp']
                humidity = data['main']['humidity']
                wind = data['wind']['speed']

                return (
                    f"╔══════ WEATHER FOR {city.upper()} ══════╗\n"
                    f"║ Conditions: {weather.title()}\n"
                    f"║ Temperature: {temp}°C\n"
                    f"║ Humidity: {humidity}%\n"
                    f"║ Wind Speed: {wind} m/s\n"
                    f"╚════════════════════════════════╝"
                )
            else:
                return f">>> ⚠️ Could not retrieve weather for {city}. Error: {response.status_code}"
        except Exception as e:
            return f">>> [Weather Error] {str(e)}"

    def ask_gemini(self, query):
        """Send query to Gemini AI and get response"""
        try:
            chat = self.gemini_model.start_chat()
            result = chat.send_message(query)
            return result.text.strip()
        except Exception as e:
            return f"[Gemini Error] {str(e)}"

    def fetch_news(self):
        """Fetch latest news headlines"""
        try:
            response = requests.get(NEWS_API_URL)
            news_data = response.json()
            if news_data["status"] == "ok":
                articles = news_data["articles"][:5]
                news = "╔══════════════ TODAY'S TOP NEWS ══════════════╗\n"
                for i, article in enumerate(articles, 1):
                    news += f"║ {i}. {article['title']}\n"
                news += "╚═══════════════════════════════════════════════╝"
                return news
            else:
                return ">>> ⚠️ Failed to fetch news."
        except Exception as e:
            return f">>> [News Error] {str(e)}"

    def run_diagnostics(self):
        """Run and return system diagnostics"""
        import psutil

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            diagnostics = (
                "╔══════════════ SYSTEM DIAGNOSTIC ══════════════╗\n"
                f"║ CPU Usage: {cpu_percent}%\n"
                f"║ RAM: {memory.percent}% used ({memory.used / (1024 ** 3):.2f} GB / {memory.total / (1024 ** 3):.2f} GB)\n"
                f"║ Disk: {disk.percent}% used ({disk.used / (1024 ** 3):.2f} GB / {disk.total / (1024 ** 3):.2f} GB)\n"
                f"║ Battery: {self.get_battery_info()}\n"
                f"║ Temperature: {self.get_random_temp()}°C\n"
                "║ Threat Level: LOW\n"
                "╚═══════════════════════════════════════════════╝"
            )

            return diagnostics
        except ImportError:
            return (
                "╔══════════════ SYSTEM DIAGNOSTIC ══════════════╗\n"
                f"║ CPU: OK\n"
                f"║ RAM: OK\n"
                f"║ GPU: Not Found\n"
                f"║ Battery: {self.get_battery_info()}\n"
                f"║ Temperature: {self.get_random_temp()}°C\n"
                "║ Threat Level: LOW\n"
                "╚═══════════════════════════════════════════════╝"
            )

    def get_battery_info(self):
        """Get battery information or simulation"""
        import psutil

        try:
            battery = psutil.sensors_battery()
            if battery:
                return f"{battery.percent}% {'Charging' if battery.power_plugged else 'Discharging'}"
            else:
                return "No battery detected"
        except (ImportError, AttributeError):
            # Simulate battery percentage
            return f"{random.randint(70, 100)}%"

    def get_random_temp(self):
        """Return a random temperature for effect"""
        return random.randint(38, 45)

    def read_log_file(self):
        """Read and return the contents of the log file"""
        try:
            if not os.path.exists(LOG_FILE):
                return ">>> No log file found."

            with open(LOG_FILE, "r") as log_file:
                lines = log_file.readlines()

            # Get last 10 lines or all if fewer
            last_lines = lines[-10:] if len(lines) > 10 else lines

            log_output = "╔══════════════ COMMAND LOG ══════════════╗\n"
            for line in last_lines:
                log_output += f"║ {line.strip()}\n"
            log_output += "╚═══════════════════════════════════════════╝"

            return log_output
        except Exception as e:
            return f">>> Error reading log file: {str(e)}"

    def simulate_self_destruct(self):
        """Simulate self-destruct sequence for fun with visual effects"""
        # Flash the screen red a few times
        orig_bg = self.text_area.cget("bg")
        for _ in range(3):
            self.text_area.config(bg="#660000")
            self.text_area.update()
            time.sleep(0.2)
            self.text_area.config(bg=orig_bg)
            self.text_area.update()
            time.sleep(0.2)

        return (
            "╔══════════ SELF DESTRUCT SEQUENCE ══════════╗\n"
            "║ 💣 SELF DESTRUCT SEQUENCE INITIATED\n"
            "║ Countdown: 5...\n"
            "║ Countdown: 4...\n"
            "║ Countdown: 3...\n"
            "║ Countdown: 2...\n"
            "║ Countdown: 1...\n"
            "║ Just kidding! 😎 Self destruct cancelled.\n"
            "╚═══════════════════════════════════════════════╝"
        )

    def diagnostic_shortcut(self, event=None):
        """Run diagnostics via keyboard shortcut"""
        response = self.run_diagnostics()
        self.typewriter_effect(response)

    def typewriter_effect(self, text):
        """Display text with typewriter effect"""
        if not text:
            return

        delay = 0.001  # Fast typing speed for hacker feel
        for char in text:
            self.text_area.insert(tk.END, char)
            self.text_area.see(tk.END)
            self.text_area.update()
            time.sleep(delay)

    def quit_app(self, event=None):
        """Exit the application with animation"""
        # Flash shutdown message
        shutdown_msg = "\n>>> Terminating session...\n>>> Goodbye, Operator."
        self.typewriter_effect(shutdown_msg)
        self.text_area.update()

        # Fade out effect
        alpha = 1.0
        while alpha > 0:
            alpha -= 0.1
            self.root.attributes("-alpha", alpha)
            self.root.update()
            time.sleep(0.05)

        self.root.destroy()


if __name__ == "__main__":
    # Create log file if it doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as log_file:
            log_file.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log file created\n")

    root = tk.Tk()
    app = CypherApp(root)
    root.mainloop()