import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("300x150")

# Create a ttk.Style object
#style = ttk.Style()

# Configure a custom style for the Progressbar
#style.theme_use("default")  # You can experiment with different themes
#style.configure("Custom.Horizontal.TProgressbar",
#                troughcolor="lightgray",  # Background color (track)
#                background="#ff8000")       # Foreground color (bar)

# Create a Progressbar widget with the custom style
progress = ttk.Progressbar(root, 
                           orient="horizontal", length=200, mode="determinate")
progress.config(troughcolor="lightgray")  # Background color (track)
progress.configure(background="#ff8000")  # Foreground color (bar)

#progress = ttk.Progressbar(root, style="Custom.Horizontal.TProgressbar",
#                           orient="horizontal", length=200, mode="determinate")
progress.pack(pady=20)

# Set the progress value
progress['value'] = 50

root.mainloop()