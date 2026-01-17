import io
import tkinter as tk
import base64
from io import BytesIO
from PIL import Image, ImageTk

# ---------------------------------------------------------
#  Base64 PNG (choose whichever one you want)
# ---------------------------------------------------------
png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAUCAYAAACEYr13AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsEAAA7BAbiRa+0AAAGHaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49J++7vycgaWQ9J1c1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCc/Pg0KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyI+PHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj48cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0idXVpZDpmYWY1YmRkNS1iYTNkLTExZGEtYWQzMS1kMzNkNzUxODJmMWIiIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIj48dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPjwvcmRmOkRlc2NyaXB0aW9uPjwvcmRmOlJERj48L3g6eG1wbWV0YT4NCjw/eHBhY2tldCBlbmQ9J3cnPz4slJgLAAACOklEQVQ4T52Tv08TYRjHP+9xR3uFBRIwGJyIIw6VssiEKSAbMqkDLICDOqiLhAkTGTH4B1igLhJ/LhgGurQRBiILQWTBiQNqArZ31/tRzuEC3tU2Gj/Tvd/v83zf9543r0inF71Py8uosRh/w9B1RkZHSSb7zjVx5/Yt7+Gjx7S0tOB5HkKIUNMZQghyuRxra5+ZnX3+2xgfH/NOTk68f2Fz84s3OfkkpMkAtm0DkMlkeJVeRI2pQPgkAsj/yKNpGg/u38MwTW4MDCAHiz5+eE9XIkF3dzeeF3R8ZFmmvl7BMEzy+TwL86lwQFSNkkgkiMevBuWqFAoF3r19Ew4AOD09xTRNZmae4dg2Ul1dyNd1neHhYeLxLoDqAbIs03Oth3K5jJDCs7Btm/b2S7iuA9UCXNdFURT6+vsrrRAHBxpUC1AUBcuySKVe4joOkiSFfNMs0Xu9l46OywCE3f/gjxM4jkMkEmFi4m6lFaLmL8iyjOM4ZFZXaw6xs/MKzc3Nfn3IBSRJwnVdsrlszWtsamqitfUCnAWoquovZBnLslBVlenpp6HGSg4PDwCQCoWfZLNZNjY20DSNSCRCuVxmZ+cr29vbbG1tsb+/X9mPEP785aGhmywtvUaNRtn9tktjYyOlUokXc3NYloVZKpFMJhkZGa3M8Ak+zampSW99fS0o1eT4+NibGB/zn/MZxWKR73t7tLVdDMrgb3T+LYTg6OgIXS8ivICzsrLCwnyKWEPDeXEtDMNgcHCQX5wiS4oqTftoAAAAAElFTkSuQmCC"
#png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAUCAYAAACEYr13AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsAAAA7AAWrWiQkAAAGHaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49J++7vycgaWQ9J1c1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCc/Pg0KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyI+PHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj48cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0idXVpZDpmYWY1YmRkNS1iYTNkLTExZGEtYWQzMS1kMzNkNzUxODJmMWIiIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIj48dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPjwvcmRmOkRlc2NyaXB0aW9uPjwvcmRmOlJERj48L3g6eG1wbWV0YT4NCjw/eHBhY2tldCBlbmQ9J3cnPz4slJgLAAACdUlEQVQ4T32Ty08TURSHvzPTNoEhaQJbNSEh+GBcFx8liAuMQV0ZJCAbRF2oO5GV7CTxwV5jNP4VvrqrRAgPF2yI2EqKrHgK6bSducx10XbitOKXnExyzj2/+7vnZGRi4rH++OE9lmXxP3zfR2vNy1evaW9vD/Jyo/+6TqfTWJaFk89TLJVCjVW01uTzeT59TpFMdgX5SCwWIxqNopSi88xZkskkCKBD/fjaR8QgkegM5WX45qBOpVK0tbXx5u07Zma+on0fEQkdREAQ9vf38ZSHW3I51dFBBEApxZGjx9jY2OTB/XtEIiYHB35YIEADguu69PZeKguICAdKAZp4PE48Hqe5ubm2M0BrTS6Xw7KsssDfOI7DufNJxh+No9F1s0BAeYrR0RE8z6sXsKwmvi0uMDw8VFsK0Fqzu7tLLBbDqC0ahlAsFvm1tnZorK+vo5RCROodOI5DItHJ4FDFga55Q2Vek5NPcF33Xw4M8k6ebDZDNpMhm82GI5Mh+zOL8jzEMOodNDQ08GNlhfm5udpSgIjQ2NhINBKpF1BK0dLSQodt19uvoLVmeXkZ3/frBQqFAsdPnGTs4Vh5jf9AKcXdO7fLa9SVW6pfy7JYXJhnYKC/pi2M4zjY9mkM1/PY2dmhVCohIogInuuyvb0dxN7eb3zfD0UVWVpa0isr32ltbcXzFFf6LpPs6mJk5BZojYiwurrK1NQLTNMMfjLHcejuvkDEtm1s2wZgdnYW0zTZ2tziSzqNrghsbW9hGHUbB0B09fHA9PQ01672EY1GKRQKwSHTNGlqagrmRMVBT8/FsEAul+P5s6eIgBxyY5VioUAi0ckfei5GiUfXXccAAAAASUVORK5CYII="


# ---------------------------------------------------------
#  Decode base64 → Tkinter PhotoImage
# ---------------------------------------------------------
def load_png_from_b64(b64_string):
    raw = base64.b64decode(b64_string)  
    pil_image = Image.open(io.BytesIO(raw))
    
    # Convert PIL Image to PhotoImage via PPM format
    ppm_buffer = io.BytesIO()
    pil_image.save(ppm_buffer, format='PPM')
    return tk.PhotoImage(data=ppm_buffer.getvalue())

# ---------------------------------------------------------
#  Build UI
# ---------------------------------------------------------
root = tk.Tk()
root.title("Two Sections Example")

# Load image once (reuse for both buttons)
icon_img = load_png_from_b64(png_b64)

# ---------------------------------------------------------
#  Section 1 — System default
# ---------------------------------------------------------
frame_default = tk.Frame(root)
frame_default.pack(fill="x", padx=10, pady=10)

btn_default = tk.Button(frame_default, image=icon_img, text=" Default Section ",
                        compound="left")
btn_default.pack(pady=5)

# ---------------------------------------------------------
#  Section 2 — Black background
# ---------------------------------------------------------
frame_black = tk.Frame(root, bg="black")
frame_black.pack(fill="x", padx=10, pady=10)

btn_black = tk.Button(frame_black, image=icon_img, text=" Black Section ",
                      compound="left", bg="black", fg="white",
                      activebackground="gray20", activeforeground="white")
btn_black.pack(pady=5)

root.mainloop()