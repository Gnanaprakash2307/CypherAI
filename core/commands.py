import tkinter as tk
import webbrowser
from config.settings import SHORTCUTS
from core.ai_integration import fetch_news, generate_response

class CommandProcessor:
    def __init__(self, terminal_window):
        self.window = terminal_window
        self.entry = None
        self.create_terminal_ui()

    def create_terminal_ui(self):
        self.entry = tk.Entry(self.window, font=("Courier", 14), bg="#111", fg="#00FF00", insertbackground="#00FF00")
        self.entry.pack(fill=tk.BOTH, expand=True)
        self.entry.focus()

        self.entry.bind("<Return>", self.process_command)
        self.entry.bind("<Control-s>", self.save_notes)
        self.entry.bind("<Control-n>", self.show_news)

    def process_command(self, event=None):
        command = self.entry.get().lower().strip()
        if command == "clear":
            self.clear_terminal()
        elif command == "help":
            self.show_help()
        elif command.startswith("generate"):
            self.generate_ai_response(command)
        elif command.startswith("news"):
            self.show_news()
        else:
            self.display_message(f"Unknown command: {command}")

    def save_notes(self, event=None):
        # Example function for saving notes
        self.display_message("Saving notes...")

    def show_help(self):
        self.display_message("HELP: Available commands - clear, help, generate, news")

    def generate_ai_response(self, command):
        # Here we could call an API like Gemini or other AI APIs
        query = command.replace("generate ", "")
        ai_response = generate_response(query)  # Assuming a function generates the AI response
        self.display_message(ai_response)

    def show_news(self, event=None):
        news = fetch_news()  # Fetch news via Gemini API or any other source
        self.display_message(news)

    def clear_terminal(self):
        # Clear the terminal UI (optional)
        self.entry.delete(0, tk.END)

    def display_message(self, message):
        self.entry.insert(tk.END, f"\n{message}\n")
        self.entry.see(tk.END)
