import tkinter as tk
from src.canvasprogressbar import CanvasProgressBar

# Example Usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Canvas-Based Progress Bar")

    progress_bar = CanvasProgressBar(root)
    progress_bar.canvas.grid(row=0, column=0, padx=20, pady=20)  # Ensuring it's placed with grid()

    lbl = tk.Label(root, text=f"colour: {progress_bar.fg}")
    lbl.grid(row=3, column=0, pady=10)

    def increase_progress():
        for i in range(101):
            root.after(i * 20, lambda v=i: progress_bar.update_progress(v))

    def change_colour():
        # Toggle the color between green and orange
        colour = "orange" if progress_bar.canvas.itemcget(progress_bar.progress_rect, "fill") == "green" else "green"
        progress_bar.set_bar_colour(colour)
        lbl.config(text=f"colour: {colour}")

    tk.Button(root, text="Start Progress", command=increase_progress).grid(row=1, column=0, pady=10)
    tk.Button(root, text="Change Colour", command=change_colour).grid(row=2, column=0, pady=10)
    
    root.mainloop()