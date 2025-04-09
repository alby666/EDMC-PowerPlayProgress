import tkinter as tk
from tkinter.ttk import Progressbar, Style

def toggle_colors():
    global toggle
    if toggle:
        # Apply black background and orange bar
        style.configure("black.Orange.Horizontal.TProgressbar", 
                        background="orange", 
                        troughcolor="black")
        progressbar.config(style="black.Orange.Horizontal.TProgressbar")
    else:
        # Reset to the system default style (empty string resets the style)
        progressbar.config(style="")
    toggle = not toggle

# Initialize the main window
root = tk.Tk()
root.title("Toggle Progress Bar Colors")

# Initialize the style
style = Style()
style.theme_use('default')  # Use default system styling

# Initialize the toggle state
toggle = True

# Create the progress bar
progressbar = Progressbar(root, orient="horizontal", length=300, mode="determinate")
progressbar.pack(pady=20)
progressbar["value"] = 50  # Example progress value

# Create a button to toggle colors
toggle_button = tk.Button(root, text="Toggle Colors", command=toggle_colors)
toggle_button.pack(pady=10)

# Run the application
root.mainloop()