from EDMCLogging import get_plugin_logger # type: ignore # noqa: N813
from consts import PLUGIN_NAME, plugin_version
from config import appname # type: ignore # noqa: N813


logger = get_plugin_logger(f"{appname}.{PLUGIN_NAME}")

class RecentJournal:

    #These are the journal entries we are not interested in - we want meritible actions and the "powerplaymerits" entries
    noise = {"friends","receivetext","powerplay","powerplaycollect", "powerplayrank","powerplay","reservoirreplenished","sendtext", "receivetext", "communitygoal", "wingadd", "wingjoin", "winginvite", "wingleave", "wingremove", "wingcancel"}

    HISTORY_DEPTH: int = 100

    def __init__(self) -> None:
        self.__journal_entries_log: list = []

    def add_entry(self, entry: dict) -> None:
        if entry['event'].lower() not in self.noise:
            #logger.debug(f"journal entries type: {type(self.__journal_entries_log)}")
            self.__journal_entries_log.append(entry)
        # Keep only the last HISTORY_DEPTH entries
        if len(self.__journal_entries_log) > self.HISTORY_DEPTH:
            self.__journal_entries_log = self.__journal_entries_log[-self.HISTORY_DEPTH:]

    @property
    def isScan(self) -> bool:
        #logger.debug(f"journal entries 1: {self.__journal_entries_log[1]['event'].lower()}")
        #logger.debug(f"journal entries 2: {self.__journal_entries_log[2]['event'].lower()}")
        #logger.debug(f"journal entries 0: {self.__journal_entries_log[0]['MeritsGained']}")
        return ((self.__journal_entries_log[1].get("event", "").lower() == "shiptargeted"
             or self.__journal_entries_log[2].get("event", "").lower() == "shiptargeted")
            and 0 >= int(self.__journal_entries_log[0].get("MeritsGained", -1)) <= 40)
    
    @property
    def isBounty(self) -> bool:
        return (self.__journal_entries_log[1].get("event", "").lower() == "bounty" 
                and int(self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits"))
    
    @property
    def isPowerPlayDelivery(self) -> bool:
        return ((self.__journal_entries_log[1].get("event", "").lower() == "powerplaydelivery" 
                or self.__journal_entries_log[2].get("event", "").lower() == "powerplaydelivery")
                and int(self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits"))

    
    @property
    def isDonationMission(self) -> bool:
        return (self.__journal_entries_log[1].get("event", "").lower() == "missionaccepted" 
                and self.__journal_entries_log[1].get("Name").lower() == "mission_altruismcredits"
                and int(self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits"))
    
    @property
    def isUnknown(self) -> bool:
        #will eventually need a number of NOT ORs here
        return (not self.isScan and not self.isBounty and not self.isPowerPlayDelivery)
    
