"""
EDMC plugin.

It aggregates the PowerPlay progress of the current session and the current system.
It displays the progress in a progress bar and a label, and allows the user to copy the progress to the clipboard.
"""
from __future__ import annotations

import math
import locale
import re
import requests
import platform
import semantic_version  # type: ignore # noqa: N813
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from consts import PLUGIN_NAME, mined_heading, plugin_version
from recentjournal import RecentJournal
from sessionprogress import SessionProgress
from socials import Socials
from rares import Rares
from systemprogress import SystemProgress
from multiHyperlinkLabel import MultiHyperlinkLabel
from canvasprogressbar import CanvasProgressBar
from PIL import Image, ImageOps

import myNotebook as nb  # type: ignore # noqa: N813
from config import appname, config # type: ignore # noqa: N813
from EDMCLogging import get_plugin_logger # type: ignore # noqa: N813
from theme import theme # type: ignore # noqa: N813
import plug # type: ignore # noqa: N813

logger = get_plugin_logger(f"{appname}.{PLUGIN_NAME}")

class PowerPlayProgress:
    """
    ClickCounter implements the EDMC plugin interface.

    It adds a button to the EDMC UI that displays the number of times it has been clicked, and a preference to set
    the number directly.
    """

    bar_colours = ['Green', 'Orange', 'Match theme']
    
    def __init__(self) -> None:
        # Be sure to use names that wont collide in our config variables
        #Preferences declarations
        self.options_view_progress_bar = tk.BooleanVar(value=bool(config.get_bool('options_view_progress_bar', default=True)))
        self.options_view_totals = tk.BooleanVar(value=bool(config.get_bool('options_view_totals', default=True)))
        self.options_view_merits_by_systems = tk.BooleanVar(value=bool(config.get_bool('options_view_merits_by_systems', default=True)))
        self.options_view_merits_by_activities = tk.BooleanVar(value=bool(config.get_bool('options_view_merits_by_activities', default=True)))
        self.options_view_detail_mined_commodities = tk.BooleanVar(value=bool(config.get_bool('options_view_detail_mined_commodities', default=True)))
        self.options_view_powerplay_commodities = tk.BooleanVar(value=bool(config.get_bool('options_view_powerplay_commodities', default=True)))
        self.options_view_powerplay_commodities_by_type = tk.BooleanVar(value=bool(config.get_bool('options_view_powerplay_commodities_by_type', default=True)))
        self.options_view_powerplay_commodities_by_system = tk.BooleanVar(value=bool(config.get_bool('options_view_powerplay_commodities_by_system', default=True)))
        self.options_view_export_format = tk.StringVar(value=config.get_str('options_view_export_format', default='Text'))
        self.options_view_bar_colour = tk.StringVar(value=config.get_str('options_view_bar_colour', default=self.bar_colours[2]))
        self.options_view_socials = tk.BooleanVar(value=bool(config.get_bool('options_view_socials', default=True)))
        self.options_custom_format = tk.StringVar(value=config.get_str('options_custom_format', default='[{system}]({system_url}) - {merits} - {state}:{progress}'))

        self.pb: CanvasProgressBar = None
        self.powerplay_level_label: tk.Label = tk.Label()
        self.powerplay_level_value = 0
        self.current_session: SessionProgress = SessionProgress()
        self.previous_session: SessionProgress = SessionProgress()
        self.starting_merits = 0
        self.total_merits = 0
        self.systems: list[SystemProgress] = []
        self.power_play_list_labels: list[tk.Label] = []
        self.power_play_hpl_labels: list[MultiHyperlinkLabel] = []
        self.current_system: SystemProgress = SystemProgress()
        self.frame: tk.Frame = tk.Frame()
        self.total_merits_label: tk.Label = tk.Label()    
        self.total_session_merits: tk.Label = tk.Label()
        self.total_since_merits: tk.Label = tk.Label()
        self.total_prev_merits: tk.Label = tk.Label()
        self.powerplay_commodities_label = tk.Label()
        self.merits_by_systems_label: tk.Label = tk.Label()
        self.copy_button: tk.Button = tk.Button()
        self.reset_button_button: tk.Button = tk.Button()
        self.reset_session_button: tk.Button = tk.Button()
        self.rares_button: tk.Button = tk.Button()
        self.recent_journal_log: RecentJournal = RecentJournal()
        self.socials_link_discord: MultiHyperlinkLabel = MultiHyperlinkLabel()
        self.socials_link_reddit: MultiHyperlinkLabel = MultiHyperlinkLabel()
        self.socials_frame: tk.Frame = tk.Frame()
        self.mertits_by_system_frame: tk.Frame = tk.Frame()
        self.progressbar_frame: tk.Frame = tk.Frame()
        self.totals_frame: tk.Frame = tk.Frame()
        self.pp_commods_frame: tk.Frame = tk.Frame()
        self.merits_by_activty_frame: tk.Frame = tk.Frame()
        self.buttons_frame: tk.Frame = tk.Frame()
        self.socials_power_label: tk.Label = tk.Label()

        self.flex_row = 7
        self.last_merits_gained = 0
        self.rares_window = None  # Track open rares window
        logger.info("PowerPlayProgress instantiated")

    def on_load(self) -> str:
        """
        on_load is called by plugin_start3 below.

        It is the first point EDMC interacts with our code after loading our module.

        :return: The name of the plugin, which will be used by EDMC for logging and for the settings window
        """
        return PLUGIN_NAME

    def on_unload(self) -> None:
        """
        on_unload is called by plugin_stop below.

        It is the last thing called before EDMC shuts down. Note that blocking code here will hold the shutdown process.
        """
        self.on_preferences_closed("", False)  # Save our prefs

    def setup_preferences(self, parent: nb.Notebook, cmdr: str, is_beta: bool) -> nb.Frame | None:
        """
        setup_preferences is called by plugin_prefs below.

        It is where we can setup our own settings page in EDMC's settings window. Our tab is defined for us.

        :param parent: the tkinter parent that our returned Frame will want to inherit from
        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        :return: The frame to add to the settings window
        """
        frame = nb.Frame(parent)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        MultiHyperlinkLabel(frame, text="EDMC Power Play Progress", background=nb.Label().cget('background'),
                    url='https://github.com/alby666/EDMC-PowerPlayProgress/releases', underline=True) \
            .grid(row=0, padx=5, pady= 10, sticky=tk.W)    

        MultiHyperlinkLabel(frame, text="Report an Issue", background=nb.Label().cget('background'),
                    url='https://github.com/alby666/EDMC-PowerPlayProgress/issues/new/choose', underline=True) \
            .grid(row=0, column=1, padx=5, pady= 10, sticky=tk.E)    

        notebook = ttk.Notebook(frame)    
        notebook.add(self.get_display_prefs_tab(notebook), text='Display options')
        notebook.grid(row=10, columnspan=2, pady=0, sticky=tk.NSEW)

        return frame

    def get_display_prefs_tab(self, parent: nb.Notebook) -> nb.Frame:
        frame = nb.Frame(parent)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)

        row_count = 0
        
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_progress_bar, text="Show/hide Progress Bar").grid(row=row_count, column=0, padx=5, pady=2, sticky="w")
        nb.Checkbutton(frame, variable=self.options_view_totals, text="Show/hide Totals").grid(row=row_count, column=1, padx=5, pady=2, sticky="w")
        row_count += 1
        ttk.Separator(frame).grid(row=row_count, pady=10, sticky=tk.EW, columnspan=4)
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_socials, text="Show/hide Socials Links").grid(row=row_count, column=0, padx=5, pady=2, sticky="w")
        row_count += 1
        ttk.Separator(frame).grid(row=row_count, pady=10, sticky=tk.EW, columnspan=4)
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_merits_by_systems, text="Show/hide Merits by Systems").grid(row=row_count, column=0, padx=5, pady=2, sticky="w")
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_merits_by_activities, text="Show/hide Merits by Activities").grid(row=row_count, column=0, padx=5, pady=2, sticky="w")
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_detail_mined_commodities, text="Detail mined commodities").grid(row=row_count, column=0, padx=20, pady=2, sticky="w")
        row_count += 1
        ttk.Separator(frame).grid(row=row_count, pady=10, sticky=tk.EW, columnspan=4)
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_powerplay_commodities, text="Show/hide Powerplay commodities").grid(row=row_count, column=0, padx=5, pady=2, sticky="w")
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_powerplay_commodities_by_type, text="By type").grid(row=row_count, column=0, padx=20, pady=2, sticky="w")
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_powerplay_commodities_by_system, text="By system").grid(row=row_count, column=0, padx=20, pady=2, sticky="w")
        row_count += 1
        ttk.Separator(frame).grid(row=row_count, pady=10, sticky=tk.EW, columnspan=4)
        row_count += 1

        export_options = ['Text', 'Discord', 'Custom']
        nb.Label(frame,
            text='Copy to Clipboard format:\n' +
                    '   Text - plain ascii text\n' +
                    '   Discord - markup format, better suited for pasting to Discord\n' +
                    '   Custom - custom format, one line by system',
            justify=tk.LEFT) \
        .grid(row=row_count, padx=5, column=0, sticky=tk.NW, columnspan=2)
        row_count+= 1
        nb.OptionMenu(
            frame,
            self.options_view_export_format,
            self.options_view_export_format.get(),
            *export_options
        ).grid(row=row_count, padx=15, sticky=tk.W, columnspan=2)
        row_count += 1

        nb.Label(frame,
            text='Custom format:',
            justify=tk.LEFT) \
        .grid(row=row_count, padx=5, column=0, sticky=tk.NW, columnspan=2)
        row_count += 1
        nb.EntryMenu(frame, textvariable=self.options_custom_format, width=50) \
            .grid(row=row_count, column=0, padx=15, sticky=tk.W, columnspan=2)
        row_count += 1

        nb.Label(frame,
            text='Progress bar colour:\n' +
                    '   Green - always green\n' +
                    '   Orange - always orange\n' +
                    '   Match theme - match the EDMC theme colour',
            justify=tk.LEFT) \
        .grid(row=row_count-4, column=2, padx=5, sticky=tk.NW, columnspan=2)
        nb.OptionMenu(
            frame,
            self.options_view_bar_colour,
            self.options_view_bar_colour.get(),
            *self.bar_colours
        ).grid(row=row_count-3, column=2, padx=15, sticky=tk.W, columnspan=2)

        return frame
    
    def on_preferences_closed(self, cmdr: str, is_beta: bool) -> None:
        """
        on_preferences_closed is called by prefs_changed below.

        It is called when the preferences dialog is dismissed by the user.

        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        """
        # You need to cast to `int` here to store *as* an `int`, so that
        # `config.get_int()` will work for re-loading the value.
        config.set('options_view_progress_bar', bool(self.options_view_progress_bar.get()))
        config.set('options_view_totals', bool(self.options_view_totals.get()))
        config.set('options_view_merits_by_systems', bool(self.options_view_merits_by_systems.get()))
        config.set('options_view_merits_by_activities', bool(self.options_view_merits_by_activities.get()))
        config.set('options_view_detail_mined_commodities', bool(self.options_view_detail_mined_commodities.get()))
        config.set('options_view_powerplay_commodities', bool(self.options_view_powerplay_commodities.get()))
        config.set('options_view_powerplay_commodities_by_type', bool(self.options_view_powerplay_commodities_by_type.get()))
        config.set('options_view_powerplay_commodities_by_system', bool(self.options_view_powerplay_commodities_by_system.get()))
        config.set('options_view_export_format', str(self.options_view_export_format.get()))
        config.set('options_view_bar_colour', str(self.options_view_bar_colour.get()))
        config.set('options_view_socials', bool(self.options_view_socials.get()))
        config.set('options_custom_format', str(self.options_custom_format.get()))
        
        if self.options_view_bar_colour.get() == self.bar_colours[2]: # Match theme
            self.pb.set_bar_colour('green' if config.get_int('theme') == 0 else 'orange')
        else:
            self.pb.set_bar_colour(self.options_view_bar_colour.get().lower())
        
        if self.total_merits > 0: self.Update_Ppp_Display()

    def NextRankDifference(self, currentRank: int) -> int:
        """
        Reutrn the difference between the current rank and the next rank.
        """
        if currentRank == 1:
            return 2000
        elif currentRank == 2:
            return 3000
        elif currentRank == 3:
            return 4000
        elif currentRank == 4:
            return 6000
        else:
            return 8000

    def CurrentRank(self, currentMerits: int) -> int:
        """
        Return the current rank.
        """
        if currentMerits < 2000:
            return 1
        elif currentMerits < 5000:
            return 2
        elif currentMerits < 9000:
            return 3
        elif currentMerits < 15000:
            return 4
        elif currentMerits < 23000:
            return 5
        else:
            return math.floor((currentMerits - 23000) // 8000) + 6
        
    def CurrentRankLowerBound(self, currentRank: int) -> int:
        """
        Return the lower bound of the current rank.
        """
        if currentRank <= 1:
            return 0
        elif currentRank == 2:
            return 2000
        elif currentRank == 3:
            return 5000
        elif currentRank == 4:
            return 9000
        elif currentRank == 5:
            return 15000
        else:
            return 15000 + (8000 * (currentRank - 5))

    def frame_text_grid(self, frame: tk.Frame, discord: bool = False) -> str:
        """
        Returns a string representing the text property of each widget in the frame,
        arranged by their grid row and column.
        If discord=True, output is formatted with Discord-friendly markdown.
        """
        if platform.system() == "Windows":
            # Windows: use \r\n line endings
            line_ending = "\r\n"
        else:
            # Non-Windows: use \n line endings
            line_ending = "\n"

        grid_map = {}
        for widget in frame.winfo_children():
            info = widget.grid_info()
            if "row" in info and "column" in info:
                row = int(info["row"])
                col = int(info["column"])
                text = ""
                if hasattr(widget, "cget"):
                    try:
                        text = widget.cget("text")
                    except tk.TclError:
                        text = ""
                grid_map.setdefault(row, {})[col] = text

        result_lines = []
        for row in sorted(grid_map.keys()):
            cols = grid_map[row]
            if discord:
                # Discord: bold for first column, bullet for indented, tab for others
                line_parts = []
                for col in sorted(cols.keys()):
                    cell = cols[col]
                    if col == 0 and cell.strip().startswith("-"):
                        line_parts.append(f"{cell.strip()}")
                    elif col == 0:
                        line_parts.append(f"### {cell}")
                    else:
                        line_parts.append(cell)
                line = "\t".join(line_parts)
                if not line.startswith("-"): line += " ###"
            else:
                line = "\t".join(str(cols.get(col, "")) for col in sorted(cols.keys()))
            result_lines.append(line)
        return line_ending.join(result_lines) + line_ending

    def copy_to_clipboard_text(self):
        if not self.options_view_totals.get() and not self.options_view_merits_by_systems.get() and not self.options_view_powerplay_commodities.get() and not self.options_view_merits_by_activities.get():
            messagebox.showinfo("No data to copy", "No data to copy to clipboard. Try showing somthing first!")
            return
        # Clear the clipboard and append the label's text
        self.frame.clipboard_clear()
        if self.options_view_totals.get(): 
            self.frame.clipboard_append(self.frame_text_grid(self.totals_frame, discord=False))
        if self.options_view_merits_by_systems.get() and len(self.systems) > 0: 
            self.frame.clipboard_append(self.frame_text_grid(self.mertits_by_system_frame, discord=False))
        if self.options_view_powerplay_commodities.get() and (self.current_session.total_commodities_collected > 0 or self.current_session.total_commodities_delivered > 0): 
            self.frame.clipboard_append(self.frame_text_grid(self.pp_commods_frame, discord=False))
        if self.options_view_merits_by_activities.get() and self.current_session.activities.get_total_merits() > 0: 
            self.frame.clipboard_append(self.frame_text_grid(self.merits_by_activty_frame, discord=False))
        self.frame.update()  # Ensure clipboard updates

    def copy_to_clipboard_discord(self):
        if not self.options_view_totals.get() and not self.options_view_merits_by_systems.get() and not self.options_view_powerplay_commodities.get() and not self.options_view_merits_by_activities.get():
            messagebox.showinfo("No data to copy", "No data to copy to clipboard. Try showing somthing first!")
            return
        # Clear the clipboard and append the label's text
        self.frame.clipboard_clear()
        if self.options_view_totals.get(): 
            self.frame.clipboard_append(self.frame_text_grid(self.totals_frame, discord=True))
        if self.options_view_merits_by_systems.get() and len(self.systems) > 0: 
            self.frame.clipboard_append(self.frame_text_grid(self.mertits_by_system_frame, discord=True))
        if self.options_view_powerplay_commodities.get() and (self.current_session.total_commodities_collected > 0 or self.current_session.total_commodities_delivered > 0): 
            self.frame.clipboard_append(self.frame_text_grid(self.pp_commods_frame, discord=True))
        if self.options_view_merits_by_activities.get() and self.current_session.activities.get_total_merits() > 0: 
            self.frame.clipboard_append(self.frame_text_grid(self.merits_by_activty_frame, discord=True))
        self.frame.update()  # Ensure clipboard updates

    def copy_to_clipboard_custom_format(self) -> None:
        progress_format = self.options_custom_format.get()
        self.frame.clipboard_clear()
        for system in self.systems:
            if system.earnings > 0:
                fmt_args = {
                    'system': system.system,
                    'system_url': self.system_url(system.system),
                    'state': system.power_play_state,
                    'progress': f"{round(system.power_play_state_control_progress * 100, 2)}%",
                    'merits': system.earnings,
                }
                try:
                    progress_text = progress_format.format(**fmt_args)
                    self.frame.clipboard_append(progress_text + "\n")
                except KeyError as ex:
                    messagebox.showerror(
                        "Format Error",
                        f"Missing key in format: {ex}\nAvailable keys: {list(fmt_args.keys())}"
                    )

    def version_check(self) -> str:
        try:
            req = requests.get(url='https://api.github.com/repos/alby666/EDMC-PowerPlayProgress/releases/latest')
            data = req.json()
            if req.status_code != requests.codes.ok:
                raise requests.RequestException
        except (requests.RequestException, requests.JSONDecodeError) as ex:
            logger.error('Failed to parse GitHub release info', exc_info=ex)
            return ''

        plugin_ver = semantic_version.Version(plugin_version)
        version = semantic_version.Version(data['tag_name'][1:])
        if version > plugin_ver:
            return str(version)
        return ''

    def system_url(self, system: str) -> str | None:
        """Dispatch a system URL to the configured handler."""
        return plug.invoke(
            config.get_str('system_provider', default='EDSM'), 'EDSM', 'system_url', system
        )
    
    def reset_progress(self) -> None:
        """
        Reset the progress of the current session.
        """
        response = messagebox.askyesno(
            title="Reset Progress",
            message="Are you sure you want to reset ALL the progress in this session?",
            icon=messagebox.WARNING,
        )
        if response:
            self.current_session.earned_merits = 0
            self.previous_session = SessionProgress()
            for sys in self.systems:
                sys.earnings = 0
            self.current_session.commodities = []
            self.current_session.commodities_delivered_systems = []
            self.current_session.commodities_delivered_types = []
            self.current_session.activities = SessionProgress.Activities()
            self.Update_Ppp_Display()

    def show_nearest_rares_window(self) -> None:
        """
        Opens a window showing the 5 nearest rare goods to the given system.
        """
        # Check if window is already open
        if self.rares_window is not None and self.rares_window.winfo_exists():
            # Bring existing window to front
            self.rares_window.lift()
            self.rares_window.focus()
            return
        
        # Get sorted rares
        rares = Rares()
        sorted_rares = rares.get_nearest_to(self.current_system.position.x, self.current_system.position.y, self.current_system.position.z)[:10]  # Top 10

        # Create window
        win = tk.Toplevel()
        self.rares_window = win  # Store reference
        win.title(f"Nearest Rare Commodities - {self.current_system.system}")
        win.resizable(False, False)
        win.overrideredirect(True)  # Hide the system title bar
        
        # Clear reference when window is destroyed
        def on_window_close():
            self.rares_window = None
            win.destroy()
        
        win.protocol("WM_DELETE_WINDOW", on_window_close)
        
        # Position window offset from main EDMC window (multi-monitor aware)
        try:
            # Get main window dimensions and position
            main_window = self.frame.winfo_toplevel()
            main_x = main_window.winfo_x()
            main_y = main_window.winfo_y()
            main_width = main_window.winfo_width()
            main_height = main_window.winfo_height()
            
            # Get virtual root dimensions (handles multi-monitor setups)
            # These give the full desktop including all monitors
            virt_x = main_window.winfo_vrootx()
            virt_y = main_window.winfo_vrooty()
            virt_width = main_window.winfo_vrootwidth()
            virt_height = main_window.winfo_vrootheight()
            
            # Calculate screen bounds (handles negative coordinates for secondary monitors)
            screen_left = virt_x
            screen_right = virt_x + virt_width
            screen_top = virt_y
            screen_bottom = virt_y + virt_height
            
            # Default window size estimate
            win_width = 650
            win_height = 300
            
            # Calculate position: try right side first, then left
            right_x = main_x + main_width + 10
            if right_x + win_width <= screen_right:
                # Room on the right
                win_x = right_x
            else:
                # Put on the left
                left_x = main_x - win_width - 10
                if left_x >= screen_left:
                    win_x = left_x
                else:
                    # Fallback: center on main window
                    win_x = main_x + (main_width - win_width) // 2
            
            # Vertical position: align with top of main window, but keep on screen
            win_y = max(screen_top, main_y)
            if win_y + win_height > screen_bottom:
                win_y = max(screen_top, screen_bottom - win_height)
            
            win.geometry(f"+{win_x}+{win_y}")
        except Exception:
            pass  # If positioning fails, use default
        
        # Apply styling to match main window
        bg_color = self.frame.cget("bg")
        # Get foreground color from an existing label in the frame
        try:
            fg_color = self.powerplay_level_label.cget("fg")
        except:
            fg_color = "black"  # Default fallback
        win.configure(bg=bg_color)
        
        # Create custom title bar
        title_bar = tk.Frame(win, bg=bg_color, height=30, cursor="fleur")
        title_bar.grid(row=0, column=0, columnspan=7, sticky="ew", padx=0, pady=0)
        title_bar.grid_propagate(False)
        title_bar.columnconfigure(0, weight=1)
        
        # Variables for window dragging
        drag_data = {"x": 0, "y": 0}
        
        def start_drag(event):
            drag_data["x"] = event.x_root - win.winfo_x()
            drag_data["y"] = event.y_root - win.winfo_y()
        
        def drag_window(event):
            x = event.x_root - drag_data["x"]
            y = event.y_root - drag_data["y"]
            win.geometry(f"+{x}+{y}")
        
        # Title label
        title_fg_color = fg_color if config.get_int('theme') == 0 else "white"
        title_lbl = tk.Label(title_bar, text=f"Nearest Rare Commodities - {self.current_system.system}", bg=bg_color, fg=title_fg_color, font=("Arial", 8), cursor="fleur", anchor=tk.W)
        title_lbl.pack(side=tk.LEFT, padx=1, pady=1, fill=tk.BOTH, expand=True)
        theme.register(title_lbl)
        
        # Bind drag events to title bar and title label
        title_bar.bind("<Button-1>", start_drag)
        title_bar.bind("<B1-Motion>", drag_window)
        title_lbl.bind("<Button-1>", start_drag)
        title_lbl.bind("<B1-Motion>", drag_window)
                        
        # Close button
        close_btn = tk.Label(title_bar, text="X", bg=bg_color, fg=fg_color, cursor="hand2", font=("Arial", 10, "bold"))
        close_btn.pack(side=tk.RIGHT, padx=2)
        close_btn.bind("<Button-1>", lambda e: win.destroy())
        theme.register(close_btn)
                
        # Column headers (now at row 1)
        headers = ["Commodity", "System", "Station", "Max Pad Size", "Stock", "Distance (ly)"]
        for col, header in enumerate(headers):
            lbl = tk.Label(win, text=header, font=("Arial", 10, "bold"), bg=bg_color, fg=fg_color)
            lbl.grid(row=1, column=col if col <= 1 else col + 1, padx=5, pady=5, sticky="nsew")
            theme.register(lbl)

        size_mapping = {
            1: "Small",
            2: "Medium",
            3: "Large"
        }

        # Create copy icon from base64 PNG
        import base64
        import io

        png_b64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAUCAYAAACEYr13AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsAAAA7AAWrWiQkAAAGHaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49J++7vycgaWQ9J1c1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCc/Pg0KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyI+PHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj48cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0idXVpZDpmYWY1YmRkNS1iYTNkLTExZGEtYWQzMS1kMzNkNzUxODJmMWIiIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIj48dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPjwvcmRmOkRlc2NyaXB0aW9uPjwvcmRmOlJERj48L3g6eG1wbWV0YT4NCjw/eHBhY2tldCBlbmQ9J3cnPz4slJgLAAACOklEQVQ4T52Tv08TYRjHP+9xR3uFBRIwGJyIIw6VssiEKSAbMqkDLICDOqiLhAkTGTH4B1igLhJ/LhgGurQRBiILQWTBiQNqArZ31/tRzuEC3tU2Gj/Tvd/v83zf9543r0inF71Py8uosRh/w9B1RkZHSSb7zjVx5/Yt7+Gjx7S0tOB5HkKIUNMZQghyuRxra5+ZnX3+2xgfH/NOTk68f2Fz84s3OfkkpMkAtm0DkMlkeJVeRI2pQPgkAsj/yKNpGg/u38MwTW4MDCAHiz5+eE9XIkF3dzeeF3R8ZFmmvl7BMEzy+TwL86lwQFSNkkgkiMevBuWqFAoF3r19Ew4AOD09xTRNZmae4dg2Ul1dyNd1neHhYeLxLoDqAbIs03Oth3K5jJDCs7Btm/b2S7iuA9UCXNdFURT6+vsrrRAHBxpUC1AUBcuySKVe4joOkiSFfNMs0Xu9l46OywCE3f/gjxM4jkMkEmFi4m6lFaLmL8iyjOM4ZFZXaw6xs/MKzc3Nfn3IBSRJwnVdsrlszWtsamqitfUCnAWoquovZBnLslBVlenpp6HGSg4PDwCQCoWfZLNZNjY20DSNSCRCuVxmZ+cr29vbbG1tsb+/X9mPEP785aGhmywtvUaNRtn9tktjYyOlUokXc3NYloVZKpFMJhkZGa3M8Ak+zampSW99fS0o1eT4+NibGB/zn/MZxWKR73t7tLVdDMrgb3T+LYTg6OgIXS8ivICzsrLCwnyKWEPDeXEtDMNgcHCQX5wiS4oqTftoAAAAAElFTkSuQmCC"

        png_data = base64.b64decode(png_b64)
        pil_image = Image.open(io.BytesIO(png_data))
        
        # Convert PIL Image to PhotoImage via PPM format
        ppm_buffer = io.BytesIO()
        pil_image.save(ppm_buffer, format='PPM')
        copy_icon = tk.PhotoImage(data=ppm_buffer.getvalue())

        # Data rows (starting at row 2)
        for row, rare in enumerate(sorted_rares, start=2):
            # Calculate distance from current system position
            dx = rare.coordinates.x - self.current_system.position.x
            dy = rare.coordinates.y - self.current_system.position.y
            dz = rare.coordinates.z - self.current_system.position.z
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            
            tk.Label(win, text=rare.name, bg=bg_color, fg=fg_color).grid(row=row, column=0, padx=5, pady=2)
            MultiHyperlinkLabel(win, compound=tk.RIGHT, url=self.system_url(rare.system), 
                    popup_copy=True, name=f"system{re.sub(r'[^a-zA-Z0-9]', '', rare.system)}", 
                    text=f"{rare.system}", background=bg_color, foreground="blue" if config.get_int('theme') == 0 else "white").grid(row=row, column=1, padx=5, pady=2)
            
            # Copy button for system name (after System column)
            def make_copy_handler(system_name):
                def copy_system():
                    win.clipboard_clear()
                    win.clipboard_append(system_name)
                    win.update()
                return copy_system
            
            copy_btn = tk.Label(win, image=copy_icon, bg=bg_color, cursor="hand2")
            copy_btn.image = copy_icon  # Keep a reference to prevent garbage collection
            copy_btn.grid(row=row, column=2, padx=5, pady=2)
            copy_btn.bind("<Button-1>", lambda e, handler=make_copy_handler(rare.system): handler())
            theme.register(copy_btn)
            
            tk.Label(win, text=rare.stationName, bg=bg_color, fg=fg_color).grid(row=row, column=3, padx=5, pady=2)
            tk.Label(win, text=size_mapping.get(rare.maxLandingPadSize), bg=bg_color, fg=fg_color).grid(row=row, column=4, padx=5, pady=2)
            tk.Label(win, text=str(rare.count or "-"), bg=bg_color, fg=fg_color).grid(row=row, column=5, padx=5, pady=2)
            tk.Label(win, text=f"{distance:.2f}", bg=bg_color, fg=fg_color).grid(row=row, column=6, padx=5, pady=2)

        # Make columns expand equally
        for col in range(len(headers)):
            win.grid_columnconfigure(col, weight=1)

        #theme.apply(win)


    def reset_session_progress(self) -> None:
        """
        Reset the progress of the current session except for total merits.
        """
        response = messagebox.askyesno(
            title="Reset Session Progress",
            message="Are you sure you want to reset the Total Merit this session?",
            icon=messagebox.WARNING,
        )
        if response:
            #self.previous_session = self.current_session
            #self.current_session = SessionProgress()
            self.starting_merits = self.total_merits
            self.Update_Ppp_Display()

    def setup_main_ui(self, parent: tk.Frame) -> tk.Frame:
        """
        Create our entry on the main EDMC UI.

        :param parent: EDMC main window Tk
        :return: Our frame
        """
        current_row = 0
        self.frame = tk.Frame(parent)
        self.frame.grid_columnconfigure(0, weight=1)
        self.powerplay_level_label = tk.Label(self.frame, text="PowerPlay Progress: Awaiting data", justify=tk.CENTER)
        self.powerplay_level_label.grid(row=current_row, column=0, columnspan=2)
        current_row += 1

        try:
            update_version = self.version_check()
            #update_version = '0.9.1'  # for testing
            if update_version != '':
                url = f"https://github.com/alby666/EDMC-PowerPlayProgress/releases/tag/v{update_version}"
                update_link = MultiHyperlinkLabel(self.frame, text=f"Version {update_version} available", foreground="blue", cursor="hand2", url=url)
                update_link.grid(row=current_row, columnspan=2, sticky="N")
                current_row += 1
        except Exception as ex:
            # Swallow any exceptions here, we don't want to crash the plugin if we can't check for updates
            logger.error('Failed to check for updates', exc_info=ex)

        # progressbar
        self.progressbar_frame = tk.Frame(self.frame)
        self.progressbar_frame.grid_columnconfigure(0, weight=1)
        self.progressbar_frame.grid(row=current_row, column=0, sticky="NSEW")
        self.pb = CanvasProgressBar(
            self.progressbar_frame,
            width=230,
            fg="green" if config.get_int("theme") == 0 else "orange"
        )
        # place the progressbar
        self.pb.canvas.grid(column=0, row=current_row, columnspan=2)
        self.pb.update_progress(50)
        current_row += 1

        #Socials
        self.socials_frame = tk.Frame(self.frame)
        self.socials_frame.grid(row=current_row, column=0, columnspan=2, sticky="NSEW")
        current_row += 1
        self.socials_frame.grid_columnconfigure(0, weight=1)
        self.socials_frame.grid_columnconfigure(1, weight=1)
        self.socials_frame.grid_columnconfigure(2, weight=1)
        self.socials_link_reddit = MultiHyperlinkLabel(self.socials_frame, text=f"Reddit", foreground="blue", cursor="hand2")
        self.socials_power_label = tk.Label(self.socials_frame, text="PowerPlay Progress", justify=tk.CENTER)
        self.socials_link_discord = MultiHyperlinkLabel(self.socials_frame, text=f"Discord", foreground="blue", cursor="hand2")
        self.socials_link_reddit.grid(row=current_row, column=0)
        self.socials_power_label.grid(row=current_row, column=1)
        self.socials_link_discord.grid(row=current_row, column=2)
        current_row += 1

        self.totals_frame = tk.Frame(self.frame)
        self.totals_frame.grid(row=current_row, column=0, columnspan=2, sticky="NSEW")
        self.total_merits_label = tk.Label(self.totals_frame, text=f"Total Merits: 345345")
        current_row += 1
        self.total_session_merits = tk.Label(self.totals_frame, text=f"Total Merits this sessiona: 345345")
        current_row += 1
        self.total_since_merits = tk.Label(self.totals_frame, text="Total Merits since last dock/death: 23423")
        current_row += 1
        self.total_prev_merits = tk.Label(self.totals_frame, text="Total Merits since previous dock/death: N/A")
        current_row += 1

        self.mertits_by_system_frame = tk.Frame(self.frame)
        self.mertits_by_system_frame.grid_columnconfigure(0, weight=0)
        self.mertits_by_system_frame.grid_columnconfigure(1, weight=2)
        self.mertits_by_system_frame.grid_columnconfigure(2, weight=1)
        self.mertits_by_system_frame.grid(row=current_row, column=0, columnspan=2, sticky="NSEW")
        self.merits_by_systems_label = tk.Label(self.mertits_by_system_frame, text="Merits by Systems:")
        current_row += 1
        self.flex_row = current_row

        self.pp_commods_frame = tk.Frame(self.frame)
        self.pp_commods_frame.grid_columnconfigure(0, weight=0)
        self.pp_commods_frame.grid_columnconfigure(1, weight=2)
        self.pp_commods_frame.grid_columnconfigure(2, weight=1)
        self.pp_commods_frame.grid(row=current_row, column=0, columnspan=2, sticky="NSEW")
        self.powerplay_commodities_label = tk.Label(self.pp_commods_frame, text="PowerPlay Commodities (collected/delivered): 34/56")
        current_row += 1

        self.merits_by_activty_frame = tk.Frame(self.frame)
        self.merits_by_activty_frame.grid_columnconfigure(0, weight=0)
        self.merits_by_activty_frame.grid_columnconfigure(1, weight=2)
        self.merits_by_activty_frame.grid_columnconfigure(2, weight=1)
        self.merits_by_activty_frame.grid(row=current_row, column=0, columnspan=2, sticky="NSEW")
        current_row += 1

        self.buttons_frame = tk.Frame(self.frame)
        self.buttons_frame.grid_columnconfigure(0, weight=0)
        self.buttons_frame.grid_columnconfigure(1, weight=0)
        self.buttons_frame.grid_columnconfigure(2, weight=0)
        self.buttons_frame.grid_columnconfigure(3, weight=1)
        self.buttons_frame.grid(row=current_row, column=0, columnspan=2, sticky="NSEW")
        self.copy_button = tk.Button(
            self.buttons_frame,
            text="Copy",
            command=self.copy_to_clipboard_text
        )
        self.reset_button = tk.Button(
            self.buttons_frame,
            text="Reset",
            command=self.reset_progress
        )
        self.reset_session_button = tk.Button(
            self.buttons_frame,
            text="Reset Session",
            command=self.reset_session_progress
        )
        self.rares_button = tk.Button(
            self.buttons_frame, 
            text="Rares", 
            command=self.show_nearest_rares_window
        )
        current_row += 1

        #hide them for now
        self.progressbar_frame.grid_remove()
        self.mertits_by_system_frame.grid_remove()
        self.totals_frame.grid_remove()
        self.pp_commods_frame.grid_remove()
        self.merits_by_activty_frame.grid_remove()
        self.pb.canvas.grid_remove()
        self.socials_link_reddit.grid_remove()
        self.socials_link_discord.grid_remove()
        self.socials_power_label.grid_remove()
        self.buttons_frame.grid_remove()
        
        return self.frame

    def Update_Ppp_Display(self) -> None:
        """
        Update the display with the current session and system data.
        """
        # Get the system's default locale
        default_locale = locale.getlocale()
        # Set the locale to the system's default
        locale.setlocale(locale.LC_ALL, '.'.join(default_locale))

        ## Update the progress bar and label with the current session data
        if self.options_view_progress_bar.get():
            self.progressbar_frame.grid()
            self.pb.canvas.grid()
            self.powerplay_level_label.grid()
            self.powerplay_level_label.config(text=f"PowerPlay Level: {self.current_session.power_play_rank} -> {self.current_session.power_play_rank + 1}", justify=tk.CENTER)
            self.pb.update_progress(round((self.total_merits - self.CurrentRankLowerBound(self.current_session.power_play_rank)) / self.NextRankDifference(self.current_session.power_play_rank) * 100, 2))

            if self.options_view_bar_colour.get() == self.bar_colours[2]: # Match theme
                self.pb.set_bar_colour('green' if config.get_int('theme') == 0 else 'orange')
            else: # orange or green
                self.pb.set_bar_colour(self.options_view_bar_colour.get().lower())
        else:
            self.powerplay_level_label.grid_remove()
            self.progressbar_frame.grid_remove()
            self.pb.canvas.grid_remove()
            self.pb.canvas.grid_remove()

        #Socials
        if self.options_view_socials.get() and self.current_session.power_play != '':
            links = Socials.get_links(self.current_session.power_play)
            if links != "":
                self.socials_link_reddit.configure(url=links.get('reddit'))
                self.socials_link_discord.configure(url=links.get('discord'))
                self.socials_power_label.config(text=self.current_session.power_play)
                self.socials_frame.grid()
                self.socials_link_reddit.grid(column=0)
                self.socials_power_label.grid(column=1)
                self.socials_link_discord.grid(column=2)
            else:
                self.socials_link_reddit.grid_remove()
                self.socials_link_discord.grid_remove()
                self.socials_power_label.grid_remove()
                self.socials_frame.grid_remove()
        else:
            self.socials_link_reddit.grid_remove()
            self.socials_link_discord.grid_remove()
            self.socials_power_label.grid_remove()
            self.socials_frame.grid_remove()

        if self.options_view_totals.get():
            self.totals_frame.grid()
            self.total_merits_label.grid(column=0, sticky=tk.W)
            self.total_session_merits.grid(column=0, sticky=tk.W)
            self.total_since_merits.grid(column=0, sticky=tk.W)
            self.total_prev_merits.grid(column=0, sticky=tk.W)
            total_str = locale.format_string("%d", round(self.total_merits, 0), grouping=True)
            self.total_merits_label.config(text=f"Total Merits:\t\t\t\t{total_str}")

            total_str = locale.format_string("%d", round(self.total_merits - self.starting_merits, 0), grouping=True)
            self.total_session_merits.config(text=f"Total Merits this session:\t\t\t{total_str}")
            
            total_str = locale.format_string("%d", round(self.current_session.earned_merits, 0), grouping=True)
            self.total_since_merits.config(text=f"Total Merits since last dock/death:\t\t{total_str}")
            
            total_str = locale.format_string("%d", round(self.previous_session.earned_merits, 0), grouping=True)
            self.total_prev_merits.config(text=f"Total Merits since previous dock/death:\t{total_str}")
        else:
            self.total_merits_label.grid_remove()
            self.total_session_merits.grid_remove()
            self.total_since_merits.grid_remove()
            self.total_prev_merits.grid_remove()
            self.totals_frame.grid_remove()
        
        ## Remove the previous labels from the list and destroy them
        for lbl in self.power_play_list_labels:
            lbl.destroy()
        self.power_play_list_labels.clear()

        for hpl in self.power_play_hpl_labels:
            hpl.destroy()
        self.power_play_hpl_labels.clear()

        cur_row = self.flex_row
        if self.options_view_merits_by_systems.get() and len(self.systems) > 0:
            if (self.total_merits - self.starting_merits) > 0:
                self.mertits_by_system_frame.grid()
                if self.current_system.earnings > 0:
                    self.merits_by_systems_label.grid(row=cur_row, column=0, sticky="w")
                else:
                    self.mertits_by_system_frame.grid_remove()
                    self.merits_by_systems_label.grid_remove()
                cur_row += 1
                for sys in self.systems:
                    if sys.earnings > 0:
                        #tab_spacing = '\t' if len(sys.system) < 12 else ''
                        control_state_change = ''
                        if sys.power_play_state_control_progress > sys.orig_power_play_state_control_progress:
                            control_state_change = ' C\u2191' # Up arrow, increasing
                        elif sys.power_play_state_control_progress < sys.orig_power_play_state_control_progress:
                            control_state_change = ' C\u2193' # Down arrow, decreasing
                        else:
                            control_state_change = ' C\u2194' # Left-right arrow, no change
                        reinforcement_state_change = ''
                        if sys.power_play_state_reinforcement > sys.orig_power_play_state_reinforcement:
                            reinforcement_state_change = ' R\u2191'
                        elif sys.power_play_state_reinforcement < sys.orig_power_play_state_reinforcement:
                            reinforcement_state_change = ' R\u2193'
                        else:
                            reinforcement_state_change = ' R\u2194'
                        undermining_state_change = ''
                        if sys.power_play_state_undermining > sys.orig_power_play_state_undermining:
                            undermining_state_change = ' U\u2191'
                        elif sys.power_play_state_undermining < sys.orig_power_play_state_undermining:
                            undermining_state_change = ' U\u2193'
                        else:
                            undermining_state_change = ' U\u2194'
                        self.mertits_by_system_frame.grid()
                        lbl = None
                        total_str = locale.format_string("%d", round(sys.earnings, 0), grouping=True)
                        hypl = MultiHyperlinkLabel(self.mertits_by_system_frame, compound=tk.RIGHT, url=self.system_url(sys.system), popup_copy=True, name=f"system{re.sub(r'[^a-zA-Z0-9]', '', sys.system)}", text=f"  - {sys.system}")
                        hypl.grid(row=cur_row, column=0, sticky="w")
                        theme.register(hypl)
                        self.power_play_hpl_labels.append(hypl)
                        hypl = None                        
                        if sys.controlling_power != '':
                            lbl = tk.Label(self.mertits_by_system_frame, text=f"{total_str} : {sys.controlling_power} : {sys.power_play_state} : {round(sys.power_play_state_control_progress * 100, 2)}%{control_state_change}{reinforcement_state_change}{undermining_state_change}")
                        else:
                            lbl = tk.Label(self.mertits_by_system_frame, text=f"{total_str}")
                        lbl.grid(row=cur_row, column=1, columnspan=2, sticky="w")
                        theme.register(lbl)
                        self.power_play_list_labels.append(lbl)
                        cur_row += 1
        else:
            self.mertits_by_system_frame.grid_remove()
            self.merits_by_systems_label.grid_remove()

        if self.options_view_powerplay_commodities.get() and (self.current_session.total_commodities_collected > 0 or self.current_session.total_commodities_delivered > 0):
            self.pp_commods_frame.grid()
            self.powerplay_commodities_label.grid(row=cur_row, column=0, columnspan=3, sticky="w")
            self.powerplay_commodities_label.config(text=f"PowerPlay Commodities (collected/delivered): {self.current_session.total_commodities_collected} t / {self.current_session.total_commodities_delivered} t")
            cur_row += 1

            if self.current_session.total_commodities_delivered > 0:
                if self.options_view_powerplay_commodities_by_type.get():
                    lbl = tk.Label(self.pp_commods_frame, text=f"Delivered By type:")
                    lbl.grid(row=cur_row, column=0, sticky="w")
                    self.power_play_list_labels.append(lbl)
                    cur_row += 1
                    for commod in self.current_session.commodities_delivered_types:
                        count = self.current_session.total_commodities_delivered_by_type(commod)
                        if count > 0:
                            lbl = tk.Label(self.pp_commods_frame, text=f"  - {commod}:\t{round(count, 0)} t")
                            lbl.grid(row=cur_row, column=0, columnspan=3, sticky="w")
                            self.power_play_list_labels.append(lbl)
                            theme.register(lbl)
                            cur_row += 1

                if self.options_view_powerplay_commodities_by_system.get():
                    lbl = tk.Label(self.pp_commods_frame, text=f"Delivered By system:")
                    lbl.grid(row=cur_row, column=0, sticky="w")
                    self.power_play_list_labels.append(lbl) 
                    cur_row += 1
                    for commod in self.current_session.commodities_delivered_systems:
                        count = self.current_session.total_commodities_delivered_by_system(commod)
                        if count > 0:
                            hypl = MultiHyperlinkLabel(self.pp_commods_frame, compound=tk.RIGHT, url=self.system_url(commod), popup_copy=True, name='system', text=f"  - {commod}")
                            hypl.grid(row=cur_row, column=0, sticky="w")
                            total_str = locale.format_string("%d", round(count, 0), grouping=True)
                            lbl = tk.Label(self.pp_commods_frame, text=f"{total_str} t")
                            lbl.grid(row=cur_row, column=1, columnspan=2, sticky="w")
                            self.power_play_list_labels.append(lbl)
                            self.power_play_hpl_labels.append(hypl)
                            theme.register(lbl)
                            theme.register(hypl)
                            cur_row += 1
        else:
            self.pp_commods_frame.grid_remove()
            self.powerplay_commodities_label.grid_remove()

        if self.options_view_merits_by_activities.get() and self.current_session.activities.get_total_merits() > 0:
            self.merits_by_activty_frame.grid()
            lbl = tk.Label(self.merits_by_activty_frame, text=f"Merits by Activity:")
            lbl.grid(row=cur_row, column=0, sticky="w")
            self.power_play_list_labels.append(lbl)
            theme.register(lbl)
            cur_row += 1
            for act in self.current_session.activities.activities:
                if act.merits > 0: 
                    lbl = tk.Label(self.merits_by_activty_frame, text=f"  - {act.activity_type}")
                    lbl.grid(row=cur_row, column=0, sticky="w")
                    self.power_play_list_labels.append(lbl)
                    lblMerits = tk.Label(self.merits_by_activty_frame, text=f"{act.merits}")
                    lblMerits.grid(row=cur_row, column=1, columnspan=2, sticky="w")
                    self.power_play_list_labels.append(lblMerits)
                    theme.register(lbl)
                    theme.register(lblMerits)
                    cur_row += 1
                    if act.activity_type == mined_heading:
                        for commod in self.current_session.activities.mined_commodities:
                            lbl = tk.Label(self.merits_by_activty_frame, text=f"      - {commod.commodity_type.title()} : {commod.merits} : {commod.tonnage} t")
                            lbl.grid(row=cur_row, column=0, sticky="w")
                            self.power_play_list_labels.append(lbl)
                            theme.register(lbl)
                            cur_row += 1
        else:
            self.merits_by_activty_frame.grid_remove()

        self.buttons_frame.grid(row=cur_row, column=0, columnspan=2, sticky="NSEW")
        if self.options_view_export_format.get() == 'Text':
            self.copy_button.config(command=self.copy_to_clipboard_text)
        elif self.options_view_export_format.get() == 'Custom':
            self.copy_button.config(command=self.copy_to_clipboard_custom_format)
        else:
            self.copy_button.config(command=self.copy_to_clipboard_discord)
        cur_row += 1
        self.copy_button.grid(row=cur_row, column=0, sticky="W", padx=2)
        self.reset_button.grid(row=cur_row, column=1, sticky="W", padx=2)
        self.reset_session_button.grid(row=cur_row, column=2, sticky="W", padx=2)
        self.rares_button.grid(row=cur_row, column=3, sticky="W", padx=2)

        theme.update(self.frame)
        theme.update(self.mertits_by_system_frame)
        theme.update(self.pp_commods_frame)
        theme.update(self.merits_by_activty_frame)
        theme.update(self.totals_frame)
        theme.update(self.buttons_frame)
