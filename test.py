import tkinter as tk

def on_enter(event):
    alt_label.grid(row=1, column=0)
    alt_label.lift()  # Bring the label to the front

def on_leave(event):
    alt_label.grid_forget()

# Create the main window
root = tk.Tk()
root.title("Hover Example")
root.geometry("300x200")

# Create a frame to organize widgets
frame = tk.Frame(root)
frame.grid(row=0, column=0, padx=50, pady=50)

# Create the primary label
label = tk.Label(frame, text="Hover over me!", font=("Arial", 14))
label.grid(row=0, column=0)

# Create the alternate label
alt_label = tk.Label(frame, text="Hello, I am an alternate label!", bg="lightyellow", font=("Arial", 10))
alt_label.grid_forget()  # Start hidden

# Bind hover events to the primary label
label.bind("<Enter>", on_enter)
label.bind("<Leave>", on_leave)

# Run the application
root.mainloop()