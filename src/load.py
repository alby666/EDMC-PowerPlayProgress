"""
EDMC plugin.

It aggregates the PowerPlay progress of the current session and the current system.
It displays the progress in a progress bar and a label, and allows the user to copy the progress to the clipboard.
"""
from __future__ import annotations

from datetime import datetime
import math
import locale
import requests
import semantic_version  # type: ignore # noqa: N813
import re
import tkinter as tk
from tkinter import ttk
from consts import PLUGIN_NAME, plugin_version, mined_heading
from recentjournal import RecentJournal
from sessionprogress import SessionProgress
from socials import Socials
from systemprogress import SystemProgress
from ttkHyperlinkLabel import HyperlinkLabel # type: ignore # noqa: N813

import myNotebook as nb  # type: ignore # noqa: N813
from config import appname, config # type: ignore # noqa: N813
from EDMCLogging import get_plugin_logger # type: ignore # noqa: N813
from theme import theme # type: ignore # noqa: N813

logger = get_plugin_logger(f"{appname}.{PLUGIN_NAME}")

class PowerPlayProgress:
    """
    ClickCounter implements the EDMC plugin interface.

    It adds a button to the EDMC UI that displays the number of times it has been clicked, and a preference to set
    the number directly.
    """

    def __init__(self) -> None:
        # Be sure to use names that wont collide in our config variables

        #Preferences declarations
        self.options_view_totals = tk.BooleanVar(value=bool(config.get_bool('options_view_totals', default=True)))
        self.options_view_merits_by_systems = tk.BooleanVar(value=bool(config.get_bool('options_view_merits_by_systems', default=True)))
        self.options_view_merits_by_activities = tk.BooleanVar(value=bool(config.get_bool('options_view_merits_by_activities', default=True)))
        self.options_view_detail_mined_commodities = tk.BooleanVar(value=bool(config.get_bool('options_view_detail_mined_commodities', default=True)))
        self.options_view_powerplay_commodities = tk.BooleanVar(value=bool(config.get_bool('options_view_powerplay_commodities', default=True)))
        self.options_view_powerplay_commodities_by_type = tk.BooleanVar(value=bool(config.get_bool('options_view_powerplay_commodities_by_type', default=True)))
        self.options_view_powerplay_commodities_by_system = tk.BooleanVar(value=bool(config.get_bool('options_view_powerplay_commodities_by_system', default=True)))
        self.options_view_export_format = tk.StringVar(value=config.get_str('options_view_export_format', default='Text'))
        self.options_view_socials = tk.BooleanVar(value=bool(config.get_bool('options_view_socials', default=True)))

        self.pb: ttk.Progressbar = ttk.Progressbar()
        self.value_label: tk.Label = tk.Label()
        self.powerplay_level_label: tk.Label = tk.Label()
        self.powerplay_level_value = 0
        self.current_session: SessionProgress = SessionProgress()
        self.previous_session: SessionProgress = SessionProgress()
        self.starting_merits = 0
        self.total_merits = 0
        self.systems: list[SystemProgress] = []
        self.power_play_list_labels: list[tk.Label] = []
        self.current_system: SystemProgress = SystemProgress()
        self.frame: tk.Frame = tk.Frame()
        self.total_merits_label: tk.Label = tk.Label()    
        self.total_session_merits: tk.Label = tk.Label()
        self.total_since_merits: tk.Label = tk.Label()
        self.total_prev_merits: tk.Label = tk.Label()
        self.powerplay_commodities_label = tk.Label()
        self.merits_by_systems_label: tk.Label = tk.Label()
        self.copy_button: tk.Button = tk.Button()
        self.recent_journal_log: RecentJournal = RecentJournal()
        self.socials_link_discord: HyperlinkLabel = HyperlinkLabel()
        self.socials_link_reddit: HyperlinkLabel = HyperlinkLabel()
        self.socials_frame: tk.Frame = tk.Frame()
        self.socials_power_label: tk.Label = tk.Label()
        self.flex_row = 7
        self.last_merits_gained = 0
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
        frame.grid(sticky=tk.NSEW)

        HyperlinkLabel(frame, text="EDMC Power Play Progress", background=nb.Label().cget('background'),
                    url='https://github.com/alby666/EDMC-PowerPlayProgress/releases', underline=True) \
            .grid(row=0, padx=5, pady= 10, sticky=tk.W)    

        HyperlinkLabel(frame, text="Report an Issue", background=nb.Label().cget('background'),
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
        frame.grid(sticky=tk.NSEW)

        row_count = 0
        
        nb.Checkbutton(frame, variable=self.options_view_socials, text="Show/hide Socials Links").grid(row=row_count, column=0, padx=5, pady=2, sticky="w")
        row_count += 1
        ttk.Separator(frame).grid(row=row_count, pady=10, sticky=tk.EW)
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_totals, text="Show/hide Totals").grid(row=row_count, column=0, padx=5, pady=2, sticky="w")
        row_count += 1
        ttk.Separator(frame).grid(row=row_count, pady=10, sticky=tk.EW)
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_merits_by_systems, text="Show/hide Merits by Systems").grid(row=row_count, column=0, padx=5, pady=2, sticky="w")
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_merits_by_activities, text="Show/hide Merits by Activities").grid(row=row_count, column=0, padx=5, pady=2, sticky="w")
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_detail_mined_commodities, text="Detail mined commodities").grid(row=row_count, column=0, padx=20, pady=2, sticky="w")
        row_count += 1
        ttk.Separator(frame).grid(row=row_count, pady=10, sticky=tk.EW)
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_powerplay_commodities, text="Show/hide Powerplay commodities").grid(row=row_count, column=0, padx=5, pady=2, sticky="w")
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_powerplay_commodities_by_type, text="By type").grid(row=row_count, column=0, padx=20, pady=2, sticky="w")
        row_count += 1
        nb.Checkbutton(frame, variable=self.options_view_powerplay_commodities_by_system, text="By system").grid(row=row_count, column=0, padx=20, pady=2, sticky="w")
        row_count += 1
        ttk.Separator(frame).grid(row=row_count, pady=10, sticky=tk.EW)
        row_count += 1

        export_options = ['Text', 'Discord']
        nb.Label(frame,
            text='Copy to Clipboard format:\n' +
                    '   Text - plain ascii text\n' +
                    '   Discord - markup format, better suited for pasting to Discord\n',
            justify=tk.LEFT) \
        .grid(row=row_count, padx=5, column=0, sticky=tk.NW)
        row_count+= 1
        nb.OptionMenu(
            frame,
            self.options_view_export_format,
            self.options_view_export_format.get(),
            *export_options
        ).grid(row=row_count, padx=15, sticky=tk.W)

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
        config.set('options_view_totals', bool(self.options_view_totals.get()))
        config.set('options_view_merits_by_systems', bool(self.options_view_merits_by_systems.get()))
        config.set('options_view_merits_by_activities', bool(self.options_view_merits_by_activities.get()))
        config.set('options_view_detail_mined_commodities', bool(self.options_view_detail_mined_commodities.get()))
        config.set('options_view_powerplay_commodities', bool(self.options_view_powerplay_commodities.get()))
        config.set('options_view_powerplay_commodities_by_type', bool(self.options_view_powerplay_commodities_by_type.get()))
        config.set('options_view_powerplay_commodities_by_system', bool(self.options_view_powerplay_commodities_by_system.get()))
        config.set('options_view_export_format', str(self.options_view_export_format.get()))
        config.set('options_view_socials', bool(self.options_view_socials.get()))
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
            
    def copy_to_clipboard_text(self):
        # Clear the clipboard and append the label's text
        self.frame.clipboard_clear()
        self.frame.clipboard_append(self.total_merits_label.cget("text"))
        self.frame.clipboard_append("\n")
        self.frame.clipboard_append(self.total_session_merits.cget("text"))
        self.frame.clipboard_append("\n")
        self.frame.clipboard_append(self.total_since_merits.cget("text"))
        self.frame.clipboard_append("\n")
        self.frame.clipboard_append(self.total_prev_merits.cget("text"))
        self.frame.clipboard_append("\n")
        #self.frame.clipboard_append(self.merits_by_systems_label.cget("text"))
        #self.frame.clipboard_append("\n")

        for lbl in self.power_play_list_labels:
            self.frame.clipboard_append(lbl.cget("text"))
            self.frame.clipboard_append("\n")
        self.frame.update()  # Ensure clipboard updates

    def copy_to_clipboard_discord(self):
        # Clear the clipboard and append the label's text
        self.frame.clipboard_clear()
        
        # Add Markdown headers and formatting for Discord
        self.frame.clipboard_append("**" + self.total_merits_label.cget("text") + "**\n")
        self.frame.clipboard_append("**" + self.total_session_merits.cget("text") + "**\n")
        self.frame.clipboard_append("**" + self.total_since_merits.cget("text") + "**\n")
        self.frame.clipboard_append("**" + self.total_prev_merits.cget("text") + "**\n")
        
        # Format labels in the power_play_list_labels list
        for lbl in self.power_play_list_labels:
            if lbl.cget("text")[0] != "\t":
                self.frame.clipboard_append(f"**" + lbl.cget("text") + "**\n")
            else:
                self.frame.clipboard_append("- " + lbl.cget("text") + "\n")  # Use bullet points
        
        self.frame.update()  # Ensure clipboard updates

    def setup_main_ui(self, parent: tk.Frame) -> tk.Frame:
        """
        Create our entry on the main EDMC UI.

        This is called by plugin_app below.

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
            update_version = version_check()
            #update_version = '0.9.1'  # for testing
            if update_version != '':
                url = f"https://github.com/alby666/EDMC-PowerPlayProgress/releases/tag/v{update_version}"
                update_link = HyperlinkLabel(self.frame, text=f"Version {update_version} available", foreground="blue", cursor="hand2", url=url)
                update_link.grid(row=current_row, columnspan=2, sticky="N")
                current_row += 1
        except Exception as ex:
            # Swallow any exceptions here, we don't want to crash the plugin if we can't check for updates
            logger.error('Failed to check for updates', exc_info=ex)

        # progressbar
        self.pb = ttk.Progressbar(
            self.frame,
            orient='horizontal',
            mode='determinate',
            length=230
        )
        # place the progressbar
        self.pb.grid(column=0, row=current_row, columnspan=3)
        self.pb['value'] = 50

        # progress label
        self.value_label = tk.Label(self.frame, text='50 %', font=("Arial", 8), justify=tk.CENTER)
        self.value_label.grid(column=0, row=current_row, columnspan=2)  # Top padding: 2 pixels
        current_row += 1

        #Socials
        self.socials_frame = tk.Frame(self.frame)
        self.socials_frame.grid(row=current_row, column=0, columnspan=2, sticky="NSEW")
        current_row += 1
        self.socials_frame.grid_columnconfigure(0, weight=1)
        self.socials_frame.grid_columnconfigure(1, weight=1)
        self.socials_frame.grid_columnconfigure(2, weight=1)
        self.socials_link_reddit = HyperlinkLabel(self.socials_frame, text=f"Reddit", foreground="blue", cursor="hand2")
        self.socials_power_label = tk.Label(self.socials_frame, text="PowerPlay Progress", justify=tk.CENTER)
        self.socials_link_discord = HyperlinkLabel(self.socials_frame, text=f"Discord", foreground="blue", cursor="hand2")
        self.socials_link_reddit.grid(row=current_row, column=0)
        self.socials_power_label.grid(row=current_row, column=1)
        self.socials_link_discord.grid(row=current_row, column=2)
        current_row += 1

        self.total_merits_label = tk.Label(self.frame, text=f"Total Merits: 345345")
        current_row += 1
        self.total_session_merits = tk.Label(self.frame, text=f"Total Merits this sessiona: 345345")
        current_row += 1
        self.total_since_merits = tk.Label(self.frame, text="Total Merits since last dock/death: 23423")
        current_row += 1
        self.total_prev_merits = tk.Label(self.frame, text="Total Merits since previous dock/death: N/A")
        current_row += 1

        self.merits_by_systems_label = tk.Label(self.frame, text="Merits by Systems:")
        current_row += 1
        self.flex_row = current_row

        self.powerplay_commodities_label = tk.Label(self.frame, text="PowerPlay Commodities (collected/delivered): 34/56")
        current_row += 1

        self.copy_button = tk.Button(
            self.frame,
            text="Copy Progress",
            command=self.copy_to_clipboard_text
        )
        current_row += 1

        #hide them for now
        self.pb.grid_remove()
        self.value_label.grid_remove()  
        self.socials_link_reddit.grid_remove()
        self.socials_link_discord.grid_remove()
        self.socials_power_label.grid_remove()
        
        return self.frame

    def Update_Ppp_Display(self) -> None:
        """
        Update the display with the current session and system data.
        """
        logger.debug("Update_Ppp_Display event")

        # Get the system's default locale
        default_locale = locale.getlocale()
        # Set the locale to the system's default
        locale.setlocale(locale.LC_ALL, default_locale[0])
        #localized_string = locale.format_string("%d", number, grouping=True)

        ## Update the progress bar and label with the current session data
        self.pb.grid()
        self.value_label.grid()  
        self.powerplay_level_label.config(text=f"PowerPlay Level: {self.current_session.power_play_rank} -> {self.current_session.power_play_rank + 1}", justify=tk.CENTER)
        self.pb['value'] = round((self.total_merits - self.CurrentRankLowerBound(self.current_session.power_play_rank)) / self.NextRankDifference(self.current_session.power_play_rank) * 100, 2)
        self.value_label.config(text=str(round(self.pb['value'], 2))+' %')
        
        #Socials
        if self.options_view_socials.get() and self.current_session.power_play != '':
            links = Socials.get_links(self.current_session.power_play)
            self.socials_link_reddit.configure(url=links.get('reddit', ''))
            self.socials_link_discord.configure(url=links.get('discord', ''))
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

        if self.options_view_totals.get():
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
        
        ## Remove the previous labels from the list and destroy them
        for lbl in self.power_play_list_labels:
            lbl.destroy()
        self.power_play_list_labels.clear()

        cur_row = self.flex_row
        if self.options_view_merits_by_systems.get() and len(self.systems) > 0:
            if (self.total_merits - self.starting_merits) > 0:
                self.merits_by_systems_label.grid(row=cur_row, column=0, sticky="w")
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

                    lbl = None
                    total_str = locale.format_string("%d", round(sys.earnings, 0), grouping=True)
                    if sys.controlling_power != '':
                        lbl = tk.Label(self.frame, text=f"  - {sys.system}:\t{total_str} : {sys.controlling_power} : {sys.power_play_state} : {round(sys.power_play_state_control_progress * 100, 2)}%{control_state_change}{reinforcement_state_change}{undermining_state_change}")
                    else:
                        lbl = tk.Label(self.frame, text=f"  - {sys.system}:\t{total_str}")
                    lbl.grid(row=cur_row, column=0, sticky="w")
                    theme.register(lbl)
                    self.power_play_list_labels.append(lbl)
                    cur_row += 1
        else:
            self.merits_by_systems_label.grid_remove()

        if self.options_view_powerplay_commodities.get() and (self.current_session.total_commodities_collected > 0 or self.current_session.total_commodities_delivered > 0):
            self.powerplay_commodities_label.grid(row=cur_row, sticky="w")
            self.powerplay_commodities_label.config(text=f"PowerPlay Commodities (collected/delivered): {self.current_session.total_commodities_collected} t/{self.current_session.total_commodities_delivered} t")
            cur_row += 1

            if  self.current_session.total_commodities_delivered > 0:
                if self.options_view_powerplay_commodities_by_type.get():
                    lbl = tk.Label(self.frame, text=f"Delivered By type:")
                    lbl.grid(row=cur_row, column=0, sticky="w")
                    self.power_play_list_labels.append(lbl)
                    cur_row += 1
                    for commod in self.current_session.commodities_delivered_types:
                        count = self.current_session.total_commodities_delivered_by_type(commod)
                        if count > 0:
                            lbl = tk.Label(self.frame, text=f"  - {commod}:\t{round(count, 0)} t")
                            lbl.grid(row=cur_row, column=0, sticky="w")
                            self.power_play_list_labels.append(lbl)
                            theme.register(lbl)
                            cur_row += 1

                if self.options_view_powerplay_commodities_by_system.get():
                    lbl = tk.Label(self.frame, text=f"Delivered By system:")
                    lbl.grid(row=cur_row, column=0, sticky="w")
                    self.power_play_list_labels.append(lbl) 
                    cur_row += 1
                    for commod in self.current_session.commodities_delivered_systems:
                        count = self.current_session.total_commodities_delivered_by_system(commod)
                        if count > 0:
                            tab_spacing = '\t' if len(commod) < 7 else ''
                            lbl = tk.Label(self.frame, text=f"  - {commod}:\t{tab_spacing}{round(count, 0)} t")
                            lbl.grid(row=cur_row, column=0, sticky="w")
                            self.power_play_list_labels.append(lbl)
                            theme.register(lbl)
                            cur_row += 1
        else:
            self.powerplay_commodities_label.grid_remove()

        if self.options_view_merits_by_activities.get() and self.current_session.activities.get_total_merits() > 0:
            lbl = tk.Label(self.frame, text=f"Merits by Activity:")
            lbl.grid(row=cur_row, column=0, sticky="w")
            self.power_play_list_labels.append(lbl)
            cur_row += 1
            for act in self.current_session.activities.activities:
                if act.merits > 0: 
                    lbl = tk.Label(self.frame, text=f"  - {act.activity_type}\t{act.merits}")
                    lbl.grid(row=cur_row, column=0, sticky="w")
                    self.power_play_list_labels.append(lbl)
                    theme.register(lbl)
                    cur_row += 1
                    if act.activity_type == mined_heading:
                        for commod in self.current_session.activities.mined_commodities:
                            lbl = tk.Label(self.frame, text=f"      - {commod.commodity_type.title()} : {commod.merits} : {commod.tonnage} t")
                            lbl.grid(row=cur_row, column=0, sticky="w")
                            self.power_play_list_labels.append(lbl)
                            theme.register(lbl)
                            cur_row += 1
            
        #self.copy_button.grid(row=cur_row)
        if self.options_view_export_format.get() == 'Text':
            self.copy_button.config(command=self.copy_to_clipboard_text)
        else:
            self.copy_button.config(command=self.copy_to_clipboard_discord)
        cur_row += 1
        self.copy_button.grid(row=cur_row, column=0, columnspan=2, sticky="W")
        theme.update(self.frame)

ppp = PowerPlayProgress()

# Note that all of these could be simply replaced with something like:
# plugin_start3 = ppp.on_load
def plugin_start3(plugin_dir: str) -> str:
    """
    Handle start up of the plugin.

    See PLUGINS.md#startup
    """
    return ppp.on_load()

def version_check() -> str:
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

def plugin_stop() -> None:
    """
    Handle shutdown of the plugin.

    See PLUGINS.md#shutdown
    """
    return ppp.on_unload()


def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> nb.Frame | None:
    """
    Handle preferences tab for the plugin.

    See PLUGINS.md#configuration
    """
    return ppp.setup_preferences(parent, cmdr, is_beta)


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """
    Handle any changed preferences for the plugin.

    See PLUGINS.md#configuration
    """
    return ppp.on_preferences_closed(cmdr, is_beta)


def plugin_app(parent: tk.Frame) -> tk.Frame | None:
    """
    Set up the UI of the plugin.

    See PLUGINS.md#display
    """
    return ppp.setup_main_ui(parent)

def journal_entry(cmdrname: str, is_beta: bool, system: str, station: str, entry: dict, state: dict) -> None:
    """
    Handle the given journal entry.

    :param cmdrname:
    :param is_beta:
    :param system:
    :param station:
    :param entry:
    :param state:
    :return: None
    """
    #logger.debug(
    #        f'cmdr = "{cmdrname}", is_beta = "{is_beta}"'
    #        f', system = "{system}", station = "{station}"'
    #        f', event = "{entry["event"]}"'
    #)

    locale.setlocale(locale.LC_ALL, '')
    new_event = False
    ppp.recent_journal_log.add_entry(entry)
    event_type = entry['event'].lower()
    match event_type:

        case 'location':
            """
            Update the current system.
            'cmdr = "xyz", is_beta = "False", system = "HIP 101587", station = "JBQ-90Q", event = "Location"'
            """
            #{"timestamp":"2025-04-08T20:23:51Z","event":"Location","DistFromStarLS":313.110615,"Docked":true,"StationName":"Pratchett Gateway","StationType":"Orbis","MarketID":3226027008,"StationFaction":{"Name":"Casual Crew"},"StationGovernment":"$government_Democracy;","StationGovernment_Localised":"Democracy","StationServices":["dock","autodock","blackmarket","commodities","contacts","exploration","missions","outfitting","crewlounge","rearm","refuel","repair","shipyard","tuning","engineer","missionsgenerated","flightcontroller","stationoperations","powerplay","searchrescue","stationMenu","shop","livery","socialspace","bartender","vistagenomics","pioneersupplies","apexinterstellar","frontlinesolutions","registeringcolonisation"],"StationEconomy":"$economy_Agri;","StationEconomy_Localised":"Agriculture","StationEconomies":[{"Name":"$economy_Agri;","Name_Localised":"Agriculture","Proportion":1.0}],"Taxi":false,"Multicrew":false,"StarSystem":"Tobala","SystemAddress":3618266663283,"StarPos":[23.34375,-42.46875,79.3125],"SystemAllegiance":"Independent","SystemEconomy":"$economy_Agri;","SystemEconomy_Localised":"Agriculture","SystemSecondEconomy":"$economy_Terraforming;","SystemSecondEconomy_Localised":"Terraforming","SystemGovernment":"$government_Democracy;","SystemGovernment_Localised":"Democracy","SystemSecurity":"$SYSTEM_SECURITY_medium;","SystemSecurity_Localised":"Medium Security","Population":4779808034,"Body":"Pratchett Gateway","BodyID":47,"BodyType":"Station",
            # "ControllingPower":"Denton Patreus","Powers":["Denton Patreus","Yuri Grom","Jerome Archer"],"PowerplayState":"Fortified","PowerplayStateControlProgress":0.278852,"PowerplayStateReinforcement":11942,"PowerplayStateUndermining":88,"Factions":[{"Name":"Revolutionary Tobala Democrats","FactionState":"None","Government":"Democracy","Influence":0.014985,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":-22.0847},{"Name":"Tobala Vision Industries","FactionState":"None","Government":"Corporate","Influence":0.00999,"Allegiance":"Empire","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0},{"Name":"Traditional Tobala Nationalists","FactionState":"None","Government":"Dictatorship","Influence":0.011988,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0},{"Name":"Tobala Gold Posse","FactionState":"None","Government":"Anarchy","Influence":0.00999,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":-18.7796},{"Name":"Tobala Jet Creative & Co","FactionState":"None","Government":"Corporate","Influence":0.034965,"Allegiance":"Federation","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":-9.51682,"RecoveringStates":[{"State":"PublicHoliday","Trend":0}]},{"Name":"Loosely Organized Lunatics","FactionState":"None","Government":"Dictatorship","Influence":0.144855,"Allegiance":"Empire","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0,"RecoveringStates":[{"State":"Blight","Trend":0}]},{"Name":"Casual Crew","FactionState":"None","Government":"Democracy","Influence":0.773227,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0,"PendingStates":[{"State":"Expansion","Trend":0}]}],"SystemFaction":{"Name":"Casual Crew"}}
            new_event = True
            logger.debug("Location event")
            found = False
            for sys in ppp.systems:
                if sys.system == system:
                    sys.earnings += ppp.current_system.earnings
                    if sys.controlling_power == '' and entry.get("ControllingPower", "") != "":
                        # If the system is found, set the original values as some scenarios it is possible to have a location event before a fsdjump event.
                        sys.orig_power_play_state_control_progress = entry["PowerplayStateControlProgress"]
                        sys.orig_power_play_state_reinforcement = entry["PowerplayStateReinforcement"]
                        sys.orig_power_play_state_undermining = entry["PowerplayStateUndermining"]
                    if entry.get("ControllingPower", "") != "":
                        sys.controlling_power = entry["ControllingPower"]
                        sys.power_play_state = entry["PowerplayState"]
                        sys.power_play_state_control_progress = entry["PowerplayStateControlProgress"]
                        sys.power_play_state_reinforcement = entry["PowerplayStateReinforcement"]
                        sys.power_play_state_undermining = entry["PowerplayStateUndermining"]
                    found = True
                    break
            if not found and entry.get("ControllingPower", "") != "":
                logger.debug(f"System not found: {system}")
                ppp.current_system = SystemProgress()
                ppp.current_system.system = system
                ppp.current_system.earnings = 0
                ppp.current_system.controlling_power = entry["ControllingPower"]
                ppp.current_system.power_play_state = entry["PowerplayState"]
                ppp.current_system.power_play_state_control_progress = entry["PowerplayStateControlProgress"]
                ppp.current_system.power_play_state_reinforcement = entry["PowerplayStateReinforcement"]
                ppp.current_system.power_play_state_undermining = entry["PowerplayStateUndermining"]
                ppp.current_system.orig_power_play_state_control_progress = entry["PowerplayStateControlProgress"]
                ppp.current_system.orig_power_play_state_reinforcement = entry["PowerplayStateReinforcement"]
                ppp.current_system.orig_power_play_state_undermining = entry["PowerplayStateUndermining"]
                ppp.systems.append(ppp.current_system)

        case 'fsdjump':
            logger.debug("fsdjump event")

            #{"timestamp":"2025-04-09T18:14:33Z","event":"FSDJump","Taxi":false,"Multicrew":false,"StarSystem":"Fusang","SystemAddress":2656177228139,"StarPos":[-12.59375,-19.03125,39.71875],"SystemAllegiance":"Federation","SystemEconomy":"$economy_HighTech;","SystemEconomy_Localised":"High Tech","SystemSecondEconomy":"$economy_Refinery;","SystemSecondEconomy_Localised":"Refinery","SystemGovernment":"$government_Democracy;","SystemGovernment_Localised":"Democracy","SystemSecurity":"$SYSTEM_SECURITY_medium;","SystemSecurity_Localised":"Medium Security","Population":4828680,"Body":"Fusang","BodyID":0,"BodyType":"Star",
            # "ControllingPower":"Yuri Grom","Powers":["Yuri Grom","Jerome Archer"],"PowerplayState":"Fortified","PowerplayStateControlProgress":0.430706,"PowerplayStateReinforcement":9232,"PowerplayStateUndermining":273,"JumpDist":9.845,"FuelUsed":0.041981,"FuelLevel":31.958019,"Factions":[{"Name":"Fusang Fortune Commodities","FactionState":"None","Government":"Corporate","Influence":0.013225,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0},{"Name":"Fusang Focus","FactionState":"Election","Government":"Dictatorship","Influence":0.080366,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0,"ActiveStates":[{"State":"Election"}]},{"Name":"Liberals of Fusang","FactionState":"Boom","Government":"Democracy","Influence":0.674466,"Allegiance":"Federation","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0,"ActiveStates":[{"State":"Boom"},{"State":"CivilLiberty"}]},{"Name":"Fusang Society","FactionState":"None","Government":"Anarchy","Influence":0.010173,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0},{"Name":"Fusang Regulatory State","FactionState":"Election","Government":"Dictatorship","Influence":0.080366,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand1;","Happiness_Localised":"Elated","MyReputation":0.0,"ActiveStates":[{"State":"CivilLiberty"},{"State":"Election"}]},{"Name":"EG Union","FactionState":"None","Government":"Dictatorship","Influence":0.10885,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":6.70655,"RecoveringStates":[{"State":"Expansion","Trend":0}]},{"Name":"Pheonix Legion","FactionState":"None","Government":"Confederacy","Influence":0.032553,"Allegiance":"Federation","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0}],"SystemFaction":{"Name":"Liberals of Fusang","FactionState":"Boom"},"Conflicts":[{"WarType":"election","Status":"active","Faction1":{"Name":"Fusang Focus","Stake":"Marchand Military Facility","WonDays":1},"Faction2":{"Name":"Fusang Regulatory State","Stake":"Francisco de Almeida Beacon","WonDays":0}}],"EDDMapColor":-65536}

            #{"timestamp":"2025-04-09T18:06:29Z","event":"FSDJump","Taxi":false,"Multicrew":false,"StarSystem":"LP 926-40","SystemAddress":422794217835,"StarPos":[-9.78125,-26.71875,45.1875],"SystemAllegiance":"Independent","SystemEconomy":"$economy_Industrial;","SystemEconomy_Localised":"Industrial","SystemSecondEconomy":"$economy_Refinery;","SystemSecondEconomy_Localised":"Refinery","SystemGovernment":"$government_Patronage;","SystemGovernment_Localised":"Patronage","SystemSecurity":"$SYSTEM_SECURITY_high;","SystemSecurity_Localised":"High Security","Population":51036582,"Body":"LP 926-40 A","BodyID":1,"BodyType":"Star",
            # "ControllingPower":"Jerome Archer","Powers":["Yuri Grom","Jerome Archer"],"PowerplayState":"Exploited","PowerplayStateControlProgress":0.361932,"PowerplayStateReinforcement":2412,"PowerplayStateUndermining":135,"JumpDist":10.94,"FuelUsed":0.062701,"FuelLevel":31.9373,"Factions":[{"Name":"Future of LP 926-40","FactionState":"CivilWar","Government":"Democracy","Influence":0.118762,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0,"ActiveStates":[{"State":"CivilWar"}]},{"Name":"Party of LP 926-40","FactionState":"None","Government":"Dictatorship","Influence":0.027944,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0},{"Name":"LP 926-40 Blue State Network","FactionState":"CivilWar","Government":"Corporate","Influence":0.118762,"Allegiance":"Federation","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0,"ActiveStates":[{"State":"CivilWar"}]},{"Name":"Law Party of LP 926-40","FactionState":"War","Government":"Dictatorship","Influence":0.122754,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0,"ActiveStates":[{"State":"War"}]},{"Name":"Knights of the Void","FactionState":"None","Government":"Patronage","Influence":0.4002,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0},{"Name":"Old Space Cowboys ABDE","FactionState":"War","Government":"Democracy","Influence":0.122754,"Allegiance":"Federation","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":0.0,"PendingStates":[{"State":"Expansion","Trend":0}],"ActiveStates":[{"State":"War"}]},{"Name":"Gilgamesh Corps Orbital Protection","FactionState":"None","Government":"Dictatorship","Influence":0.088822,"Allegiance":"Independent","Happiness":"$Faction_HappinessBand2;","Happiness_Localised":"Happy","MyReputation":3.80893}],"SystemFaction":{"Name":"Knights of the Void"},"Conflicts":[{"WarType":"civilwar","Status":"active","Faction1":{"Name":"Future of LP 926-40","Stake":"Wei's Wandering","WonDays":0},"Faction2":{"Name":"LP 926-40 Blue State Network","Stake":"Marino Metallurgic Exchange","WonDays":0}},{"WarType":"war","Status":"active","Faction1":{"Name":"Law Party of LP 926-40","Stake":"","WonDays":0},"Faction2":{"Name":"Old Space Cowboys ABDE","Stake":"Baturin Arsenal","WonDays":0}}],"EDDMapColor":-65536}
            new_event = True
            found = False
            for sys in ppp.systems:
                if sys.system == system:
                    if (entry.get("ControllingPower", "") != ""):
                        sys.controlling_power = entry["ControllingPower"]
                        sys.power_play_state = entry["PowerplayState"]
                        sys.power_play_state_control_progress = entry["PowerplayStateControlProgress"]
                        sys.power_play_state_reinforcement = entry["PowerplayStateReinforcement"]
                        sys.power_play_state_undermining = entry["PowerplayStateUndermining"]
                    found = True
                    break
            #If its a new system and it has a controlling power otherwise there is no power play to track
            if (not found) and (entry.get("ControllingPower", "") != ""):
                ppp.current_system = SystemProgress()
                ppp.current_system.system = system
                ppp.current_system.earnings = 0
                ppp.current_system.controlling_power = entry.get("ControllingPower", "")
                ppp.current_system.power_play_state = entry.get("PowerplayState", "")
                ppp.current_system.power_play_state_control_progress = entry.get("PowerplayStateControlProgress", 0)
                ppp.current_system.power_play_state_reinforcement = entry.get("PowerplayStateReinforcement", 0)
                ppp.current_system.power_play_state_undermining = entry.get("PowerplayStateUndermining", 0)
                ppp.current_system.orig_power_play_state_control_progress = entry.get("PowerplayStateControlProgress", 0)
                ppp.current_system.orig_power_play_state_reinforcement = entry.get("PowerplayStateReinforcement", 0)
                ppp.current_system.orig_power_play_state_undermining = entry.get("PowerplayStateUndermining", 0)
                ppp.systems.append(ppp.current_system)
            
        case 'died' | 'docked':
            """"
            Update the current sessiona dn start a new one.
            """""
            logger.debug("Docked or died event")
            #{"timestamp":"2025-03-29T11:57:38Z","event":"Docked","StationName":"Gelfand Dock","StationType":"Coriolis","Taxi":false,"Multicrew":false,"StarSystem":"Misisture","SystemAddress":5368172137360,"MarketID":3225950976,"StationFaction":{"Name":"Blackiron","FactionState":"Expansion"},"StationGovernment":"$government_Corporate;","StationGovernment_Localised":"Corporate","StationAllegiance":"Federation","StationServices":["dock","autodock","commodities","contacts","exploration","missions","outfitting","crewlounge","rearm","refuel","repair","shipyard","tuning","engineer","missionsgenerated","flightcontroller","stationoperations","powerplay","searchrescue","stationMenu","shop","livery","socialspace","bartender","vistagenomics","pioneersupplies","apexinterstellar","frontlinesolutions","registeringcolonisation"],"StationEconomy":"$economy_Industrial;","StationEconomy_Localised":"Industrial","StationEconomies":[{"Name":"$economy_Industrial;","Name_Localised":"Industrial","Proportion":1.0}],"DistFromStarLS":225.201053,"ActiveFine":true,"LandingPads":{"Small":17,"Medium":18,"Large":9}}
            #{"timestamp":"2025-03-29T11:42:44Z","event":"Died","KillerName":"Exobyte Corp","KillerShip":"cobramkiv","KillerRank":"Competent"}
            new_event = True
            ppp.previous_session = ppp.current_session
            ppp.current_session = SessionProgress()
            ppp.current_session.time = datetime.now()
            ppp.current_session.earned_merits = 0
            ppp.current_session.power_play = ppp.previous_session.power_play
            ppp.current_session.power_play_rank = ppp.previous_session.power_play_rank
            ppp.current_session.commodities = ppp.previous_session.commodities
            ppp.current_session.commodities_delivered_systems = ppp.previous_session.commodities_delivered_systems
            ppp.current_session.commodities_delivered_types = ppp.previous_session.commodities_delivered_types
            ppp.current_session.activities = ppp.previous_session.activities

        #"PowerplayCollect"
        #"PowerplayDeliver"
        #"PowerplayMerits"   
        #"PowerplayRank"

        case 'powerplaycollect':
            #{"timestamp":"2025-04-05T11:29:18Z","event":"PowerplayCollect","Power":"Jerome Archer","Type":"republicanfieldsupplies","Type_Localised":"Archer's Field Supplies","Count":52}
            new_event = True
            if entry["Type"] != "powerspyware":
                ppp.current_session.add_commodity(SessionProgress.Commodities(entry["Type"], entry["Type_Localised"], system, entry["Count"], 0))

        case 'powerplaydeliver':
            #{"timestamp":"2025-04-05T11:34:05Z","event":"PowerplayDeliver","Power":"Jerome Archer","Type":"republicanfieldsupplies","Type_Localised":"Archer's Field Supplies","Count":52}
            #this might be something to deal with later:
            #{"timestamp":"2025-05-04T09:48:23Z","event":"DeliverPowerMicroResources","TotalCount":1,"MicroResources":[{"Name":"powerpropagandadata","Name_Localised":"Power Political Data","Category":"ata","Count":1}],"MarketID":3930408705}
            #The mnarketid in the above refers to the stronghold carrier and not teh originating system/settelement
            #{"timestamp":"2025-05-04T09:48:23Z","event":"PowerplayDeliver","Power":"Jerome Archer","Type":"powerpropagandadata","Type_Localised":"Power Political Data","Count":1}
            new_event = True
            ppp.current_session.add_commodity(SessionProgress.Commodities(entry["Type"], entry["Type_Localised"], system, 0, entry["Count"]))

        case 'powerplaymerits':
            logger.debug("PowerplayMerits event")
            #{"timestamp":"2025-03-29T10:30:53Z","event":"PowerplayMerits","Power":"Jerome Archer","MeritsGained":20,"TotalMerits":1084567}
            #First check if EDMC was loaded after the game was started.
            new_event = True
            if ppp.current_session.power_play == '':
                ppp.current_session.power_play = entry["Power"]
                ppp.current_session.power_play_rank = ppp.CurrentRank(entry["TotalMerits"])
                ppp.starting_merits = int(entry["TotalMerits"]) - int(entry["MeritsGained"])
                ppp.total_merits = int(entry["TotalMerits"])  

                if system != '':
                    ppp.current_system = SystemProgress()
                    ppp.current_system.system = system
                    ppp.current_system.earnings = 0
                    ppp.systems.append(ppp.current_system)

            #Record the merits gained
            ppp.current_session.earned_merits += entry["MeritsGained"]
            ppp.total_merits = int(entry["TotalMerits"])
            #Apportion the merits to the appropriate system
            for sys in ppp.systems:
                if sys.system == system:
                    sys.earnings += entry["MeritsGained"]
                    break

            #Assign merits to appropriate activity...
            if ppp.recent_journal_log.isScan: ppp.current_session.activities.add_ship_scan_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isBounty: ppp.current_session.activities.add_bounty_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isPowerPlayDelivery: ppp.current_session.activities.add_powerplay_delivery_merits(entry["MeritsGained"])
            #Donations missions are a bit tricky as they can be completed after the merits are awarded.
            elif ppp.recent_journal_log.isDonationMissionMeritsFirst and not ppp.recent_journal_log.isDonationMissionMeritsSecond: 
                logger.debug(f"Donation mission merits first: {entry}")
                ppp.current_session.activities.add_donation_mission_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isScanDataLinks: ppp.current_session.activities.add_scan_data_links_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isHoloscreenHack: ppp.current_session.activities.add_holoscreen_hacks_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isRareGoods: ppp.current_session.activities.add_rare_goods_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isSalvage: ppp.current_session.activities.add_salvage_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isCartography: ppp.current_session.activities.add_cartography_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isHighValueCommditySale: ppp.current_session.activities.add_high_value_commodities_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isLowValueCommditySale: ppp.current_session.activities.add_low_value_commodities_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isExobiology: ppp.current_session.activities.add_exobiology_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isMined: ppp.current_session.activities.add_mined_merits(entry["MeritsGained"], ppp.recent_journal_log.get_mined_commodity(), ppp.recent_journal_log.get_mined_tonnage())
            elif ppp.recent_journal_log.isOnFoot: ppp.current_session.activities.add_on_foot_merits(entry["MeritsGained"])
            else: 
                ppp.recent_journal_log.writelog()
                ppp.current_session.activities.add_unknown_merits(entry["MeritsGained"])

            ppp.last_merits_gained = entry["MeritsGained"]
        case 'powerplayrank':
            #{"timestamp":"2025-03-29T10:47:35Z","event":"PowerplayRank","Power":"Jerome Archer","Rank":139}
            new_event = True
            ppp.current_session.power_play_rank = entry["Rank"]

        case 'powerplay':
            #{"timestamp":"2025-03-23T08:39:26Z","event":"Powerplay","Power":"Jerome Archer","Rank":138,"Merits":1084487,"TimePledged":12319106}
            new_event = True
            ppp.current_session.power_play = entry["Power"]
            ppp.current_session.power_play_rank = int(entry["Rank"])
            ppp.starting_merits = int(entry["Merits"])
            ppp.total_merits = int(entry["Merits"])

            if system != '':
                ppp.current_system = SystemProgress()
                ppp.current_system.system = system
                ppp.current_system.earnings = 0
                ppp.systems.append(ppp.current_system)

        case 'missioncompleted':
            # need to check for this for donation missions as they potnetially complete after the merits are awarded
            #{"timestamp":"2025-04-19T13:19:53Z","event":"MissionCompleted","Faction":"United CD-63 1560 Bureau","Name":"Mission_AltruismCredits_name",
            # "LocalisedName":"Donate 1,000,000 Cr to the cause","MissionID":1012529686,"Donation":"1000000","Donated":1000000,"FactionEffects":[{"Faction":"United CD-63 1560 Bureau","Effects":[{"Effect":"$MISSIONUTIL_Interaction_Summary_EP_up;","Effect_Localised":"The economic status of $#MinorFaction; has improved in the $#System; system.","Trend":"UpGood"}],"Influence":[{"SystemAddress":2282942829282,"Trend":"UpGood","Influence":"++"}],"ReputationTrend":"UpGood","Reputation":"++"}]}
            #{"timestamp":"2025-04-19T13:19:53Z","event":"PowerplayMerits","Power":"Jerome Archer","MeritsGained":44,"TotalMerits":1113351}
           
            new_event = True
            #logger.debug(f"Mission completed event: {entry}")
            #logger.debug(f"Mission completed event name: {entry.get('Name', '')}")
            #logger.debug(f"Mission completed event is donation: {ppp.recent_journal_log.isDonationMission}")

            if ppp.current_session.activities.get_unknown_merits() > 0 and ppp.recent_journal_log.isDonationMissionMeritsSecond:
                #Move the merits from the unknown activity to the donation mission activity
                logger.debug(f"Donation mission merits second: {entry}")
                ppp.current_session.activities.add_donation_mission_merits(ppp.last_merits_gained)
                ppp.current_session.activities.add_unknown_merits(-ppp.last_merits_gained)
                #do not process any other options for previous merits gained
                ppp.last_merits_gained = 0
            
    if ppp.total_merits > 0 and new_event: ppp.Update_Ppp_Display()