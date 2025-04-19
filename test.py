import tkinter as tk
from tkinter import ttk

def change_color():
    style.configure("green.Horizontal.TProgressbar", background="orange", troughcolor="white")

# Create the main window
root = tk.Tk()
root.title("Tkinter Progress Bar")

# Define the style
style = ttk.Style(root)
style.theme_use('default')
style.configure("green.Horizontal.TProgressbar", background="green", troughcolor="white")

# Create a progress bar with the custom style
progress = ttk.Progressbar(root, style="green.Horizontal.TProgressbar", orient="horizontal", length=300, mode="determinate")
progress.pack(pady=20)

# Set progress bar value
progress['value'] = 50  # Example value

# Create a button to change color
button = tk.Button(root, text="Change to Orange", command=change_color)
button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()