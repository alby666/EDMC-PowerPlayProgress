"""
EDMC plugin.

It aggregates the PowerPlay progress of the current session and the current system.
It displays the progress in a progress bar and a label, and allows the user to copy the progress to the clipboard.
"""
from __future__ import annotations

from datetime import datetime
import locale
import tkinter as tk
from consts import PLUGIN_NAME
from sessionprogress import SessionProgress
from systemprogress import SystemProgress

import myNotebook as nb  # type: ignore # noqa: N813
from config import appname # type: ignore # noqa: N813
from EDMCLogging import get_plugin_logger # type: ignore # noqa: N813

from powerplayprogress import PowerPlayProgress

logger = get_plugin_logger(f"{appname}.{PLUGIN_NAME}")
wait_for_multi_sell_carto_data = -1
ppp = PowerPlayProgress()

# Note that all of these could be simply replaced with something like:
# plugin_start3 = ppp.on_load
def plugin_start3(plugin_dir: str) -> str:
    """
    Handle start up of the plugin.

    See PLUGINS.md#startup
    """
    return ppp.on_load()

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
    global wait_for_multi_sell_carto_data
    locale.setlocale(locale.LC_ALL, '')
    new_event = False
    ppp.recent_journal_log.add_entry(entry)

    if wait_for_multi_sell_carto_data > 0: 
        logger.debug(f"Waiting for multi sell carto data: {wait_for_multi_sell_carto_data}")
        wait_for_multi_sell_carto_data -= 1
    if wait_for_multi_sell_carto_data == 0:
        #Now process the multi sell carto data, we have waited for 5 journal entries to be more sure we have all the data
        logger.debug("Processing multi sell carto data")
        multi_carto_merits = ppp.recent_journal_log.get_multiple_cartography()
        logger.debug(f"Multi carto merits: {ppp.recent_journal_log.get_multiple_cartography()}")
        if multi_carto_merits > 0:
            ppp.current_session.activities.add_cartography_merits(multi_carto_merits)
            ppp.current_session.activities.add_unknown_merits(-multi_carto_merits)
        wait_for_multi_sell_carto_data= -1

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
            #The mnarketid in the above refers to the stronghold carrier and not teh originating system/settelement
            #{"timestamp":"2025-05-04T09:48:23Z","event":"PowerplayDeliver","Power":"Jerome Archer","Type":"powerpropagandadata","Type_Localised":"Power Political Data","Count":1}
            new_event = True
            ppp.current_session.add_commodity(SessionProgress.Commodities(entry["Type"], entry["Type_Localised"], system, 0, entry["Count"]))


        case 'deliverpowermicroresources':
            #{"timestamp":"2025-05-04T09:48:23Z","event":"DeliverPowerMicroResources","TotalCount":1,
            # "MicroResources":[{"Name":"powerpropagandadata","Name_Localised":"Power Political Data","Category":"Data","Count":1}],"MarketID":3930408705}
            new_event = True
            for resource in entry.get("MicroResources", []):
                if str(resource["Name"]).startswith("power"):
                    ppp.current_session.add_commodity(SessionProgress.Commodities(resource["Name"], resource["Name_Localised"], system, 0, resource["Count"]))

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

                #if system != '':
                #    ppp.current_system = SystemProgress()
                #    ppp.current_system.system = system
                #    ppp.current_system.earnings = 0
                #    ppp.systems.append(ppp.current_system)

            #Record the merits gained
            found = False
            ppp.current_session.earned_merits += entry["MeritsGained"]
            ppp.total_merits = int(entry["TotalMerits"])
            #Apportion the merits to the appropriate system
            for sys in ppp.systems:
                if sys.system == system:
                    found = True
                    sys.earnings += entry["MeritsGained"]
                    break
            #Add the system to thje list of merit systems if it is not already there
            if not found:
                ppp.current_system = SystemProgress()
                ppp.current_system.system = system
                ppp.current_system.earnings = entry["MeritsGained"]
                ppp.systems.append(ppp.current_system)


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
            #MultiSellExplorationData handled separately
            elif ppp.recent_journal_log.isSingleCartography: ppp.current_session.activities.add_cartography_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isHighValueCommditySale: ppp.current_session.activities.add_high_value_commodities_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isLowValueCommditySale: ppp.current_session.activities.add_low_value_commodities_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isExobiology: ppp.current_session.activities.add_exobiology_merits(entry["MeritsGained"])
            elif ppp.recent_journal_log.isMined: ppp.current_session.activities.add_mined_merits(entry["MeritsGained"], ppp.recent_journal_log.get_mined_commodity(), ppp.recent_journal_log.get_mined_tonnage())
            elif ppp.recent_journal_log.isOnFoot: ppp.current_session.activities.add_on_foot_merits(entry["MeritsGained"])
            else: 
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
            if ppp.current_session.activities.get_unknown_merits() > 0 and ppp.recent_journal_log.isDonationMissionMeritsSecond:
                #Move the merits from the unknown activity to the donation mission activity
                logger.debug(f"Donation mission merits second: {entry}")
                ppp.current_session.activities.add_donation_mission_merits(ppp.last_merits_gained)
                ppp.current_session.activities.add_unknown_merits(-ppp.last_merits_gained)
                #do not process any other options for previous merits gained
                ppp.last_merits_gained = 0
        
        case 'multisellexplorationdata':
            #wait for 5 further journal entries before processing, 5 is a guess, even with a full page this should cover it most times
            wait_for_multi_sell_carto_data = 5

    if ppp.total_merits > 0 and new_event: ppp.Update_Ppp_Display()