"""
Type	                        Activity	                                                                                                                Implemented
Aid & Donation Missions	        Complete aid and humanitarian missions	                                                                                        Y (Donations)
Bounty Hunting	                Bounty Hunting	
Bounty Hunting	                Kill enemies	
Bounty Hunting	                Power kills - kill enemies in aquisition systems	
Cartography	                    Sell Cartography data at Universal Cartographics	
Commit Crimes	                Commit Crimes in Undermining systems	
Deliver PowerPlay Commodities	Deliver Powerplay commodities from Fortified/Stronghold systems to Power Contact in Aquisition systems"	
Deliver PowerPlay Commodities	Deliver Reinforcement commodity to Power Contacts from Stronghold/Fortified systems	
Deliver PowerPlay Commodities	Deliver to Power Contact in Undermining system after obtaining from Power Contact in any co-aligned stronghold system
Download data	                (Ody) Download Power association/Political data from settlements in aquisition, return to stronghold/fortified
Download data	                (Ody) Download Power association/Political data from settlements, return to stronghold/fortified
Download data	                (Ody) Download Power Classified data from settlements in aquisition, sell in stronghold/fortified
Download data	                (Ody) Download Power Classified data from settlements, sell in stronghold/fortified
Download data	                (Ody) Download Power research/Industrial data from settlements in aquisition, return to stronghold/fortified
Exobiology	                    turn in exobiology data to Power Contact in Reinforcement system	
High Value Commodities	        Sell trade commodities at 40% or higher	
Holoscreen hacking	            Holoscreen hacking at ports	
Low Value Commodities	        Sell commodities worth less than 500cr per ton	
Mined Commodities	            Sell mined items (not bought minable items)	
Rare Goods	                    Sell rare goods not aquired in aquisition systems	
Rare Goods	                    Sell rare goods not aquired in Reinforcement system	
Retrieve Power items	        (Ody) Retreive specific items from Power containers	
Salvage	                        Collect escape pods in Undermining systems	
Salvage	                        Collect Escape pods, take to Stronhold or Fortified systems	
Salvage	                        collect salvage and hand in to Power Contact in same Reinforcement system
Salvage	                        Hand in salvage collected in Unermining systems	
Scan datalinks	                Scan datalinks at Megaships	
Scan datalinks	                Scan datalinks at megaships in Undermining systems	
Ship scans	                    Scan ships and wakes with built-in scanner	                                                                                    Y
Upload data	                    (Ody) Upload powerplay malware	
"""

from EDMCLogging import get_plugin_logger # type: ignore # noqa: N813
from consts import PLUGIN_NAME, plugin_version
from config import appname # type: ignore # noqa: N813

logger = get_plugin_logger(f"{appname}.{PLUGIN_NAME}")

class RecentJournal:

    #These are the journal entries we are not interested in - we want meritible actions and the "powerplaymerits" entries
    noise = {"friends","receivetext","powerplay","powerplaycollect", "powerplayrank","powerplay","reservoirreplenished","sendtext", "receivetext", "communitygoal", 
             "wingadd", "wingjoin", "winginvite", "wingleave", "wingremove", "wingcancel", "startup", "loadout", "shiplocker", "statistics", "music","carrierlocation",
             "hulldamage", "repairall", "repair", "missionaccepted"}

    HISTORY_DEPTH: int = 10

    def __init__(self) -> None:
        self.__journal_entries_log: list = []

    def add_entry(self, entry: dict) -> None:
        if entry['event'].lower() not in self.noise:
            #logger.debug(f"journal entries type: {type(self.__journal_entries_log)}")
            self.__journal_entries_log.insert(0, entry)
        # Keep only the last HISTORY_DEPTH entries
        if len(self.__journal_entries_log) > self.HISTORY_DEPTH:
            self.__journal_entries_log.pop()

    @property
    def isScan(self) -> bool:
        logger.debug(f"iscan recent journal entries: {self.__journal_entries_log}")
        if len(self.__journal_entries_log) < 3:
            return False
        else:
            #logger.debug(f"journal entries 1: {self.__journal_entries_log[1].get('event', '').lower() == 'shiptargeted'}")
            #logger.debug(f"journal entries 2: {self.__journal_entries_log[2].get('event', '').lower() == 'shiptargeted'}")
            #logger.debug(f"journal entries 0: {int(self.__journal_entries_log[0].get('MeritsGained', 0)) <= 40}")
            #logger.debug(f"num: {self.__journal_entries_log[0].get('MeritsGained', 0)}")
            return ((self.__journal_entries_log[1].get("event", "").lower() == "shiptargeted"
                or self.__journal_entries_log[2].get("event", "").lower() == "shiptargeted")
                and (int(self.__journal_entries_log[0].get("MeritsGained", 0)) <= 40))
    
    @property
    def isBounty(self) -> bool:
        #logger.debug(f"isbounty recent journal entries: {self.__journal_entries_log}")
        if len(self.__journal_entries_log) < 2:
            return False
        else:
            return ((self.__journal_entries_log[1].get("event", "").lower() == "bounty" 
                     or self.__journal_entries_log[2].get("event", "").lower() == "bounty")
                    and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits")
    
    @property
    def isPowerPlayDelivery(self) -> bool:
        logger.debug(f"isPowerPlayDelivery recent journal entries: {self.__journal_entries_log}")
        if len(self.__journal_entries_log) < 3:
            return False
        else:
            return ((self.__journal_entries_log[1].get("event", "").lower() == "powerplaydeliver" 
                    or self.__journal_entries_log[2].get("event", "").lower() == "powerplaydeliver")
                    and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits")

    
    #Donation missions are usually retrospective and are not recorded in the journal until the mission is completed.
    @property
    def isDonationMission(self) -> bool:
        #logger.debug(f"isdonation 0 event: {self.__journal_entries_log[0].get('event', '')}")
        #logger.debug(f"isdonation 0 name: {self.__journal_entries_log[0].get('Name', '')}")
        #logger.debug(f"isdonation 1 event: {self.__journal_entries_log[1].get('event', '')}")
        #logger.debug(f"isDonationMission recent journal entries: {self.__journal_entries_log}")
        if len(self.__journal_entries_log) < 2:
            return False
        else:
            #Depending on server load powerplay merits events can come before mission completed or vice versa
            return (self.__journal_entries_log[0].get("event", "") == "MissionCompleted" 
                    and self.__journal_entries_log[0].get("Name", "") == "Mission_AltruismCredits_name"
                    and self.__journal_entries_log[1].get("event", "").lower() == "powerplaymerits") or (
                    self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits"
                        and self.__journal_entries_log[1].get("event", "").lower() == "missioncompleted"
                        and self.__journal_entries_log[1].get("Name", "") == "Mission_AltruismCredits_name")
    
    @property
    def isUnknown(self) -> bool:
        logger.debug(f"Unknown: {self.__journal_entries_log}")
        #will eventually need a number of NOT ORs here
        return (not self.isScan and not self.isBounty and not self.isPowerPlayDelivery)
    
