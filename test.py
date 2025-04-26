import tkinter as tk
from tkinter import ttk

def create_app():
    # Create the main application window
    root = tk.Tk()
    root.title("Checkbox Group Example")
    
    # Create a frame with an outline and label
    display_options_frame = ttk.LabelFrame(root, text="Display Options", padding=(10, 10))
    display_options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    totals_options_frame = ttk.LabelFrame(display_options_frame, text="Totals options", padding=(10, 10))
    totals_options_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    activities_options_frame = ttk.LabelFrame(display_options_frame, text="Activities options", padding=(10, 10))
    activities_options_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    powerplay_options_frame = ttk.LabelFrame(display_options_frame, text="Powerplay Commodity Options", padding=(10, 10))
    powerplay_options_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

    export_options_frame = ttk.LabelFrame(display_options_frame, text="Copy Progress Options", padding=(10, 10))
    export_options_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

    # Create checkbox variables
    totals_var = tk.BooleanVar(value=False)
    merits_by_systems_var = tk.BooleanVar(value=False)
    merits_by_activities_var = tk.BooleanVar(value=False)
    detail_mined_commodities_var = tk.BooleanVar(value=False)
    powerplay_commodities_var = tk.BooleanVar(value=False)
    by_type_var = tk.BooleanVar(value=False)
    by_system_var = tk.BooleanVar(value=False)

    # Add checkboxes and labels to the frame, aligning the checkboxes to the right
    def add_checkbox(lblFrame, row, text, lblsticky, variable):
        label = tk.Label(lblFrame, text=text, anchor="w")
        label.grid(row=row, column=0, padx=5, pady=2, sticky=lblsticky)
        checkbox = tk.Checkbutton(lblFrame, variable=variable)
        checkbox.grid(row=row, column=1, padx=5, pady=2, sticky="w")

    add_checkbox(totals_options_frame, 1, "Totals", "w", totals_var)
    add_checkbox(totals_options_frame, 2, "Merits by Systems","w", merits_by_systems_var)
    add_checkbox(activities_options_frame, 0, "Merits by Activities","w", merits_by_activities_var)
    add_checkbox(activities_options_frame, 1, "Detail mined commodities", "e", detail_mined_commodities_var)
    add_checkbox(powerplay_options_frame, 0, "Powerplay commodities", "w", powerplay_commodities_var)
    add_checkbox(powerplay_options_frame, 1, "By type", "e", by_type_var)
    add_checkbox(powerplay_options_frame, 2, "By system", "e", by_system_var)

    format_var = tk.StringVar(value="Text")

    tk.Label(export_options_frame, text="Format:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    tk.Radiobutton(export_options_frame, text="Text", variable=format_var, value="Text").grid(row=0, column=1, padx=5, pady=2, sticky="w")
    tk.Radiobutton(export_options_frame, text="Discord", variable=format_var, value="Discord").grid(row=0, column=2, padx=5, pady=2, sticky="w")


    # Start the Tkinter event loop
    root.mainloop()

# Run the application
if __name__ == "__main__":
    create_app()