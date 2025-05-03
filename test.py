import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Tkinter Grid Example")

# Create a frame to contain the labels
frame = tk.Frame(root)
frame.grid(row=0, column=0, padx=20, pady=20)

# Create two labels
label1 = tk.Label(frame, text="Label 1", font=("Arial", 14))
label2 = tk.Label(frame, text="Label 2", font=("Arial", 14))

# Place the labels in the frame using grid
label1.grid(row=0, column=0, padx=10, pady=5)
label2.grid(row=0, column=1, padx=10, pady=5)

# Center the frame in the main window
frame.grid_columnconfigure(0, weight=1)
frame.grid_columnconfigure(1, weight=1)

root.mainloop()