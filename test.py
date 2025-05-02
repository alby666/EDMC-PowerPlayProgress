import tkinter as tk
from tkinter import ttk

# Create the main window
root = tk.Tk()
root.title("Checkbutton Example")

# Create a frame
frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0)

# Function to handle the state change
def toggle_checkbutton():
    if check_var1.get():
        check2.config(state=tk.DISABLED)
    else:
        check2.config(state=tk.NORMAL)

# Define the IntVar for the checkbuttons
check_var1 = tk.IntVar()
check_var2 = tk.IntVar()

# Create the checkbuttons
check1 = ttk.Checkbutton(frame, text="Disable Second", variable=check_var1, command=toggle_checkbutton)
check2 = ttk.Checkbutton(frame, text="Second Checkbutton", variable=check_var2)

# Place the checkbuttons in the frame
check1.grid(row=0, column=0, padx=5, pady=5)
check2.grid(row=1, column=0, padx=5, pady=5)

# Run the main loop
root.mainloop()