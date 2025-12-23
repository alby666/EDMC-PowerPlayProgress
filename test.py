import tkinter as tk
from tkinter import ttk

def greet():
    result_label.config(text="Hello, Alan!")

def calculate():
    result_label.config(text=f"2 + 2 = {2 + 2}")

def show_info():
    result_label.config(text="This is a Tkinter dropdown toolbar demo.")

# Main window
root = tk.Tk()
root.title("Toolbar Dropdown Button")
root.geometry("350x200")

# Frame to simulate toolbar
toolbar = ttk.Frame(root)
toolbar.pack(pady=10)

# Create Menubutton
action_button = ttk.Menubutton(toolbar, text="Actions", direction="below")
action_menu = tk.Menu(action_button, tearoff=0)

# Add grouped actions
action_menu.add_command(label="Greet", command=greet)
action_menu.add_command(label="Calculate", command=calculate)
action_menu.add_command(label="Show Info", command=show_info)

action_button["menu"] = action_menu
action_button.pack(side="left", padx=5)

# Result label
result_label = ttk.Label(root, text="", justify="left")
result_label.pack(pady=20)

# Run the app
root.mainloop()