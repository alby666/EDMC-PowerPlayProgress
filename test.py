import tkinter as tk
from tkinter import ttk
import myNotebook as nb  # type: ignore # noqa: N813

# Create the main window
root = tk.Tk()
root.title("Separator Example")
root.geometry("300x200")

# Add a label above the separator
label_top = ttk.Label(root, text="Above the Separator")
label_top.pack(pady=10)

# Create a horizontal separator
separator = ttk.Separator(root, orient="horizontal")
separator.pack(fill="x", pady=10)

# Add a label below the separator
label_bottom = ttk.Label(root, text="Below the Separator")
label_bottom.pack(pady=10)

chk = nb.Checkbutton(root, text="Check me")
chk.pack(pady=10)

# Run the application
root.mainloop()