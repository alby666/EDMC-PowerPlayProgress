import asyncio
import tkinter as tk
#from src.canvasprogressbar import CanvasProgressBar
from rares import Rares
from tkinter import ttk

def show_nearest_rares_window() -> None:
    """
    Opens a window showing the 5 nearest rare goods to the given system.
    """
    # Get sorted rares
    rares = Rares()
    sorted_rares = asyncio.run(rares.distance_sorted_rares_async(0,0,0))[:20]  # Top 5

    # Create window
    win = tk.Toplevel()
    win.title("Nearest Rare Commodities")

    # Column headers
    headers = ["Commodity", "System", "Station", "Max Pad Size", "Stock", "Distance (ly)"]
    for col, header in enumerate(headers):
        lbl = ttk.Label(win, text=header, font=("Arial", 10, "bold"))
        lbl.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

    # Data rows
    for row, (commodity, export, distance) in enumerate(sorted_rares, start=1):
        ttk.Label(win, text=f"{commodity}").grid(row=row, column=0, padx=5, pady=2)
        ttk.Label(win, text=getattr(export, "systemName", "")).grid(row=row, column=1, padx=5, pady=2)
        ttk.Label(win, text=getattr(export, "stationName", "")).grid(row=row, column=2, padx=5, pady=2)
        ttk.Label(win, text=getattr(export, "maxLandingPadSize", "")).grid(row=row, column=3, padx=5, pady=2)
        ttk.Label(win, text=getattr(export, "stock", "")).grid(row=row, column=4, padx=5, pady=2)
        ttk.Label(win, text=f"{distance:.2f}").grid(row=row, column=5, padx=5, pady=2)

    # Make columns expand equally
    for col in range(len(headers)):
        win.grid_columnconfigure(col, weight=1)
        
# Example Usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Canvas-Based Progress Bar")

    tk.Button(root, text="Nearest rares", command=show_nearest_rares_window).grid(row=1, column=0, pady=10)
    
    
    root.mainloop()