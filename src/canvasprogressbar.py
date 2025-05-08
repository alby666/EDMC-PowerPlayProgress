import tkinter as tk

"""
A simple progress bar using Tkinter's Canvas widget.

This works around some of the limitations of the default Progressbar widget in Tkinter and the workarounds EDMC had to implement
"""

class CanvasProgressBar:
    def __init__(self, parent, width=200, height=30, bg="lightgray", fg="green", text_color="black"):
        self.width = width
        self.height = height
        self.bg = bg
        self.fg = fg
        self.text_color = text_color

        # Create Canvas for the progress bar
        self.canvas = tk.Canvas(parent, width=self.width, height=self.height, bg=self.bg, highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        # Create the progress rectangle
        self.progress_rect = self.canvas.create_rectangle(0, 0, 0, self.height, fill=self.fg, outline="")

        # Add a text label for the percentage
        self.text_label = self.canvas.create_text(self.width // 2, self.height // 2, text="0%", font=("Arial", 12, "bold"), fill=self.text_color)

    def update_progress(self, value):
        """Update progress bar and text label (value should be between 0 and 100)."""
        new_width = (self.width * value) / 100
        self.canvas.coords(self.progress_rect, 0, 0, new_width, self.height)
        self.canvas.itemconfig(self.text_label, text=f"{value}%")

    def set_bar_colour(self, colour):
        """Set the colour of the progress bar."""
        self.canvas.itemconfig(self.progress_rect, fill=colour)
        self.fg = colour