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

import tkinter as tk
from tkinter import ttk

import myNotebook as nb  # type: ignore # noqa: N813
from config import appname, config # type: ignore # noqa: N813
from EDMCLogging import get_plugin_logger # type: ignore # noqa: N813
#from ttkHyperlinkLabel import HyperlinkLabel # type: ignore # noqa: N813

# This **MUST** match the name of the folder the plugin is in.
PLUGIN_NAME: str = 'PowerPlayProgress'
plugin_version: str = '0.9.0'

logger = get_plugin_logger(f"{appname}.{PLUGIN_NAME}")

class SessionProgress(object):
    """
    Represents the progress in a single session i.e. from the last dock to the current dock or death.
    """
    def __init__(self, earned_merits=0, time=0, 
                 is_docking_event=0, power_play_rank=0, power_play=''):
        self.earned_merits = int(earned_merits)
        self.time = int(time)
        self.is_docking_event = int(is_docking_event)
        self.power_play_rank = int(power_play_rank)
        self.power_play = power_play

class SystemProgress(object):
    """
    Represents the progress in a single system
    """
    system = ''
    earnings = 0.0

class PowerPlayProgress:
    """
    ClickCounter implements the EDMC plugin interface.

    It adds a button to the EDMC UI that displays the number of times it has been clicked, and a preference to set
    the number directly.
    """

    def __init__(self) -> None:
        # Be sure to use names that wont collide in our config variables
        self.click_count = tk.StringVar(value=str(config.get_int('click_counter_count')))
        self.pb: ttk.Progressbar = ttk.Progressbar()
        self.value_label: tk.Label = tk.Label()
        self.powerplay_level_label: tk.Label = tk.Label()
        self.powerplay_level_value = 0
        self.current_session: SessionProgress = SessionProgress()
        self.previous_session: SessionProgress = SessionProgress()
        self.starting_merits = 0
        self.total_merits = 0
        self.systems: list[SystemProgress] = []
        self.current_system: SystemProgress = SystemProgress()
        self.frame: tk.Frame = tk.Frame()
        self.total_merits_label: tk.Label = tk.Label()    
        self.total_session_merits: tk.Label = tk.Label()
        self.total_since_merits: tk.Label = tk.Label()
        self.total_prev_merits: tk.Label = tk.Label()
        self.merits_by_systems_label: tk.Label = tk.Label()
        self.copy_button: tk.Button = tk.Button()
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
        #current_row = 0
        frame = nb.Frame(parent)

        # setup our config in a "Click Count: number"
        #nb.Label(frame, text='Click Count').grid(row=current_row)
        #nb.EntryMenu(frame, textvariable=self.click_count).grid(row=current_row, column=1)
        #current_row += 1  # Always increment our row counter, makes for far easier tkinter design.
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
        #config.set('click_counter_count', int(self.click_count.get()))

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
            
    def copy_to_clipboard(self):
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
        self.frame.clipboard_append(self.merits_by_systems_label.cget("text"))
        self.frame.clipboard_append("\n")

        for sys in self.systems:
            if sys.earnings > 0:
                self.frame.clipboard_append("\t" + sys.system + ": " + str(sys.earnings))
                self.frame.clipboard_append("\n")        
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

        # progressbar
        self.pb = ttk.Progressbar(
            self.frame,
            orient='horizontal',
            mode='determinate',
            length=230
        )
        # place the progressbar
        self.pb.grid(column=0, row=current_row, columnspan=3)
        self.pb['value'] = self.click_count.get()

        # progress label
        self.value_label = tk.Label(self.frame, text=self.click_count.get()+' %')
        self.value_label.grid(column=0, row=current_row, columnspan=2)
        current_row += 1

        self.total_merits_label = tk.Label(self.frame, text=f"Total Merits: 345345")
        self.total_merits_label.grid(row=current_row, column=0, sticky=tk.W)
        current_row += 1

        self.total_session_merits = tk.Label(self.frame, text=f"Total Merits this sessiona: 345345")
        self.total_session_merits.grid(row=current_row, column=0, sticky=tk.W)
        current_row += 1
        self.total_since_merits = tk.Label(self.frame, text="Total Merits since last dock/death: 23423")
        self.total_since_merits.grid(row=current_row, column=0, sticky="w")
        current_row += 1
        self.total_prev_merits = tk.Label(self.frame, text="Total Merits since previous dock/death: N/A")
        self.total_prev_merits.grid(row=current_row, column=0, sticky="w")
        current_row += 1

        self.merits_by_systems_label = tk.Label(self.frame, text="Merits by Systems:")
        self.merits_by_systems_label.grid(row=current_row, column=0, sticky="w")        
        current_row += 1

        self.copy_button = tk.Button(
            self.frame,
            text="Copy Progress",
            command=self.copy_to_clipboard
        )
        self.copy_button.grid(row=current_row, column=0, columnspan=2, sticky="W")
        current_row += 1

        #hide them for now
        self.pb.grid_remove()
        self.value_label.grid_remove()  
        self.total_merits_label.grid_remove()
        self.total_session_merits.grid_remove()
        self.total_since_merits.grid_remove()
        self.total_prev_merits.grid_remove()
        self.merits_by_systems_label.grid_remove()
        self.copy_button.grid_remove()

        return self.frame

    def Update_Ppp_Display(self) -> None:
        """
        Update the display with the current session and system data.
        """
        logger.debug("Update_Ppp_Display event")

        self.pb.grid()
        self.value_label.grid()  
        self.total_merits_label.grid()
        self.total_session_merits.grid()
        self.total_since_merits.grid()
        self.total_prev_merits.grid()
        self.merits_by_systems_label.grid()
        self.copy_button.grid()

        locale.setlocale(locale.LC_ALL, '')

        ## Update the progress bar and label with the current session data
        self.powerplay_level_label.config(text=f"PowerPlay Level: {self.current_session.power_play_rank} -> {self.current_session.power_play_rank + 1}", justify=tk.CENTER)
        self.pb['value'] = round((self.total_merits - self.CurrentRankLowerBound(self.current_session.power_play_rank)) / self.NextRankDifference(self.current_session.power_play_rank) * 100, 2)
        self.value_label.config(text=str(round(self.pb['value'], 2))+' %')
        self.total_merits_label.config(text=f"Total Merits: {round(self.total_merits, 0)}")
        self.total_session_merits.config(text=f"Total Merits this session: {round(self.total_merits - self.starting_merits, 0)}")
        self.total_since_merits.config(text=f"Total Merits since last dock/death: {round(self.current_session.earned_merits, 0)}")
        self.total_prev_merits.config(text=f"Total Merits since previous dock/death: {round(self.previous_session.earned_merits, 0)}")
        
        cur_row = 7
        for sys in self.systems:
            if sys.earnings > 0:
                lbl = tk.Label(self.frame, text=f"\t{sys.system}:\t {round(sys.earnings, 0)}")
                lbl.grid(row=cur_row, column=0, sticky="w")
                cur_row += 1
        self.copy_button.grid(row=cur_row, column=0, columnspan=2, sticky="W")

ppp = PowerPlayProgress()


# Note that all of these could be simply replaced with something like:
# plugin_start3 = ppp.on_load
def plugin_start3(plugin_dir: str) -> str:
    """
    Handle start up of the plugin.

    See PLUGINS.md#startup
    """
    return ppp.on_load()

"""
def version_check() -> str:
    try:
        req = requests.get(url='https://api.github.com/repos/alby666/EDMC-PowerPlayProgress/releases/latest')
        data = req.json()
        if req.status_code != requests.codes.ok:
            raise requests.RequestException
    except (requests.RequestException, requests.JSONDecodeError) as ex:
        logger.error('Failed to parse GitHub release info', exc_info=ex)
        return ''

    version = semantic_version.Version(data['tag_name'][1:])
    if version > plugin_version:
        return str(version)
    return ''
"""

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
    event_type = entry['event'].lower()
    match event_type:

        case 'location':
            """
            Update the current system.
            'cmdr = "Byrne666", is_beta = "False", system = "HIP 101587", station = "JBQ-90Q", event = "Location"'
            """
            logger.debug("Location event")
            found = False
            for sys in ppp.systems:
                if sys.system == system:
                    sys.earnings += ppp.current_system.earnings
                    found = True
                    break
            if not found:
                logger.debug(f"System not found: {system}")
                ppp.current_system = SystemProgress()
                ppp.current_system.system = system
                ppp.current_system.earnings = 0
                ppp.systems.append(ppp.current_system)

        case 'fsdjump':
            logger.debug("fsdjump event")
            found = False
            for sys in ppp.systems:
                if sys.system == system:
                    #sys.earnings += ppp.current_system.earnings
                    found = True
                    break
            if not found:
                ppp.current_system = SystemProgress()
                ppp.current_system.system = system
                ppp.current_system.earnings = 0
                ppp.systems.append(ppp.current_system)
            
        case 'died' | 'docked':
            """"
            Update the current sessiona dn start a new one.
            """""
            logger.debug("Docked or died event")
            #{"timestamp":"2025-03-29T11:57:38Z","event":"Docked","StationName":"Gelfand Dock","StationType":"Coriolis","Taxi":false,"Multicrew":false,"StarSystem":"Misisture","SystemAddress":5368172137360,"MarketID":3225950976,"StationFaction":{"Name":"Blackiron","FactionState":"Expansion"},"StationGovernment":"$government_Corporate;","StationGovernment_Localised":"Corporate","StationAllegiance":"Federation","StationServices":["dock","autodock","commodities","contacts","exploration","missions","outfitting","crewlounge","rearm","refuel","repair","shipyard","tuning","engineer","missionsgenerated","flightcontroller","stationoperations","powerplay","searchrescue","stationMenu","shop","livery","socialspace","bartender","vistagenomics","pioneersupplies","apexinterstellar","frontlinesolutions","registeringcolonisation"],"StationEconomy":"$economy_Industrial;","StationEconomy_Localised":"Industrial","StationEconomies":[{"Name":"$economy_Industrial;","Name_Localised":"Industrial","Proportion":1.0}],"DistFromStarLS":225.201053,"ActiveFine":true,"LandingPads":{"Small":17,"Medium":18,"Large":9}}
            #{"timestamp":"2025-03-29T11:42:44Z","event":"Died","KillerName":"Exobyte Corp","KillerShip":"cobramkiv","KillerRank":"Competent"}
            ppp.previous_session = ppp.current_session
            ppp.current_session = SessionProgress()
            ppp.current_session.time = datetime.now()
            ppp.current_session.earned_merits = 0
            ppp.current_session.power_play = ppp.previous_session.power_play
            ppp.current_session.power_play_rank = ppp.previous_session.power_play_rank

        #"PowerplayCollect"
        #"PowerplayDeliver"
        #"PowerplayMerits"   
        #"PowerplayRank"

        #case 'powerplaycollect':
        #    this.currentSession.earnings += entry["Merits"]

        #case 'powerplaydeliver':
        #    this.currentSession.earnings += entry["Merits"]

        case 'powerplaymerits':
            logger.debug("PowerplayMerits event")
            #{"timestamp":"2025-03-29T10:30:53Z","event":"PowerplayMerits","Power":"Jerome Archer","MeritsGained":20,"TotalMerits":1084567}
            ppp.current_session.earned_merits += entry["MeritsGained"]
            ppp.total_merits = entry["TotalMerits"]
            for sys in ppp.systems:
                if sys.system == system:
                    sys.earnings += entry["MeritsGained"]
                    break

        case 'powerplayrank':
            logger.debug("PowerplayRank event")
            #{"timestamp":"2025-03-29T10:47:35Z","event":"PowerplayRank","Power":"Jerome Archer","Rank":139}
            ppp.current_session.power_play_rank = entry["Rank"]

        case 'powerplay':
            logger.debug("Powerplay event")
            #{"timestamp":"2025-03-23T08:39:26Z","event":"Powerplay","Power":"Jerome Archer","Rank":138,"Merits":1084487,"TimePledged":12319106}
            ppp.current_session.power_play = entry["Power"]
            ppp.current_session.power_play_rank = entry["Rank"]
            ppp.powerplay_level_label.config(text=f"PowerPlay Level: {entry['Rank']} -> {int(entry['Rank']) + 1}", justify=tk.CENTER)
            ppp.starting_merits = entry["Merits"]
            ppp.total_merits = entry["Merits"]
            ppp.pb['value'] = round((ppp.starting_merits - ppp.CurrentRankLowerBound(ppp.current_session.power_play_rank)) / ppp.NextRankDifference(ppp.current_session.power_play_rank) * 100, 2)
            ppp.value_label.config(text=str(ppp.pb['value'])+' %')

            logger.debug(
                    f'cmdr = "{cmdrname}", power = "{entry["Power"]}"'
                    f', rank = "{entry["Rank"]}", merits = "{entry["Merits"]}"'
            )

            if system != '':
                ppp.current_system = SystemProgress()
                ppp.current_system.system = system
                ppp.current_system.earnings = 0
                ppp.systems.append(ppp.current_system)
            
    if ppp.total_merits > 0: ppp.Update_Ppp_Display()