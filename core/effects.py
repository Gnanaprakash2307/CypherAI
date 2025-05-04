import time

def typewriter_effect(text_widget, text, delay=50):
    for char in text:
        text_widget.insert("end", char)
        text_widget.see("end")
        text_widget.update_idletasks()
        time.sleep(delay / 1000.0)
