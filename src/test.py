import asyncio
import logging
import threading
import tkinter as tk
from tkinter import messagebox
#from src.canvasprogressbar import CanvasProgressBar
from rares import Rares
from tkinter import ttk

# Background cache and synchronization for rares
_rares_lock = threading.Lock()
_sorted_rares: list = []
_rares_thread: threading.Thread | None = None
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def _fetch_rares_background() -> None:
    """Background worker to fetch rares asynchronously and cache results."""
    global _sorted_rares
    try:
        r = Rares()
        result = asyncio.run(r.distance_sorted_rares_async(0, 0, 0))
        with _rares_lock:
            _sorted_rares = result[:20] if result else []
        logger.info("Fetched %d rares (background)", len(_sorted_rares))
        logger.debug("Rares preview: %r", _sorted_rares[:5])
    except Exception:
        logger.exception("Failed to fetch rares in background")


def show_nearest_rares_window() -> None:
    """
    Opens a window showing the 5 nearest rare goods to the given system.
    Uses cached results populated by the background worker.
    """
    # Use cached rares if available
    with _rares_lock:
        cached = list(_sorted_rares)

    if not cached:
        if _rares_thread and _rares_thread.is_alive():
            messagebox.showinfo("Nearest Rares", "Nearest rares are still loading. Please try again shortly.")
            return
        else:
            messagebox.showinfo("Nearest Rares", "No nearest rare data available.")
            return

    sorted_rares = cached

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
        ttk.Label(win, text=f"{commodity}").grid(row=row, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(win, text=getattr(export, "systemName", "")).grid(row=row, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(win, text=getattr(export, "stationName", "")).grid(row=row, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(win, text=getattr(export, "maxLandingPadSize", "")).grid(row=row, column=3, padx=5, pady=2)
        ttk.Label(win, text=getattr(export, "stock", "")).grid(row=row, column=4, padx=5, pady=2)
        ttk.Label(win, text=f"{distance:.2f}").grid(row=row, column=5, padx=5, pady=2)

    # Make columns expand equally
    for col in range(len(headers)):
        win.grid_columnconfigure(col, weight=1)
        


# Example Usage
if __name__ == "__main__":
    # Start background fetch thread (non-blocking)
    try:
        _rares_thread = threading.Thread(target=_fetch_rares_background, daemon=True)
        _rares_thread.start()
    except Exception:
        logger.exception("Failed to start rares background thread")

    root = tk.Tk()
    root.title("Canvas-Based Progress Bar")

    tk.Button(root, text="Nearest rares", command=show_nearest_rares_window).grid(row=1, column=0, pady=10)

    root.mainloop()