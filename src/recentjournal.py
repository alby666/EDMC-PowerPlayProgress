"""
Type	                        Activity	                                                                                                                Implemented
Aid & Donation Missions	        Complete aid and humanitarian missions	                                                                                        Y
Bounty Hunting	                Bounty Hunting		                                                                                                            Y
Bounty Hunting	                Kill enemies	                                                                                                                Y                                       
Bounty Hunting	                Power kills - kill enemies in aquisition systems		                                                                        Y
Cartography	                    Sell Cartography data at Universal Cartographics	                                                                            Y
Commit Crimes	                Commit Crimes in Undermining systems	                                                                                        Y      
Deliver PowerPlay Commodities	Deliver Powerplay commodities from Fortified/Stronghold systems to Power Contact in Aquisition systems"	                        Y
Deliver PowerPlay Commodities	Deliver Reinforcement commodity to Power Contacts from Stronghold/Fortified systems	                                            Y
Deliver PowerPlay Commodities	Deliver to Power Contact in Undermining system after obtaining from Power Contact in any co-aligned stronghold system           Y
Download data	                (Ody) Download Power association/Political data from settlements in aquisition, return to stronghold/fortified
Download data	                (Ody) Download Power association/Political data from settlements, return to stronghold/fortified
Download data	                (Ody) Download Power Classified data from settlements in aquisition, sell in stronghold/fortified
Download data	                (Ody) Download Power Classified data from settlements, sell in stronghold/fortified
Download data	                (Ody) Download Power research/Industrial data from settlements in aquisition, return to stronghold/fortified
Exobiology	                    turn in exobiology data to Power Contact in Reinforcement system	                                                            Y
High Value Commodities	        Sell trade commodities at 40% or higher	                                                                                        Y
Holoscreen hacking	            Holoscreen hacking at ports	                                                                                                    Y       
Low Value Commodities	        Sell commodities worth less than 500cr per ton	                                                                                Y
Mined Commodities	            Sell mined items (not bought minable items)	                                                                                    Y
Rare Goods	                    Sell rare goods not aquired in aquisition systems                                                                               Y	
Rare Goods	                    Sell rare goods not aquired in Reinforcement system	                                                                            Y      
Retrieve Power items	        (Ody) Retreive specific items from Power containers	
Salvage	                        Collect escape pods in Undermining systems	                                                                                    Y      
Salvage	                        Collect Escape pods, take to Stronhold or Fortified systems	                                                                    Y   
Salvage	                        collect salvage and hand in to Power Contact in same Reinforcement system                                                       Y
Salvage	                        Hand in salvage collected in Unermining systems	                                                                                Y     
Scan datalinks	                Scan datalinks at Megaships	                                                                                                    Y
Scan datalinks	                Scan datalinks at megaships in Undermining systems                                                                              Y	
Ship scans	                    Scan ships and wakes with built-in scanner	                                                                                    Y
Upload data	                    (Ody) Upload powerplay malware	
"""

import re

class RecentJournal:

    #These are the journal entries we are not interested in - we want meritible actions and the "powerplaymerits" entries
    noise = {"friends","receivetext","powerplay","powerplaycollect", "powerplayrank","powerplay","reservoirreplenished","sendtext", "receivetext", "communitygoal", 
             "wingadd", "wingjoin", "winginvite", "wingleave", "wingremove", "wingcancel", "startup", "loadout", "shiplocker", "statistics", "music","carrierlocation",
             "hulldamage", "repairall", "repair", "refuelall", "fssdiscoveryscan", "fsssignaldiscovered", "navroute", "dockingrequested", "dockinggranted",
             "storedships", "shipyard", "crimevictim"}

    rare_goods = {
        "saxonwine", "rusanioldsmokey", "thrutiscream", "uzumokulowgwings", "damnacarapaces", "bastsnakegin", "terramaterbloodbores", "livehecateseaworms", "gerasiangueuzebeer", 
        "chameleoncloth", "onionheadalphastrain", "wolffesh", "hipprotosquid", "momusbogspaniel", "taurichimes", "fujintea", "ethgrezeteabuds", "esusekucaviar", "zeesszeantgrubglue", 
        "azcancriformula42", "witchhaulkobebeef", "eraninpearlwhisky", "pantaaprayersticks", "konggaale", "tiegfriessynthsilk", "voidextractcoffee", "vherculisbodyrub", "vegaslimweed", 
        "honestypills", "haidenblackbrew", "nanomedicines", "bankiamphibiousleather", "chateaudeaegaeon", "aganipperush", "thehuttonmug", "centaurimegagin", "altairianskin", 
        "cherbonesbloodcrystals", "jotunmookah", "gilyasignatureweapons", "indibourbon", "havasupaidreamcatcher", "buckyballbeermats", "hip10175bushmeat", "ochoengchillies", 
        "ophiuchexinoartefacts", "mechucoshightea", "pavoniseargrubs", "crystallinespheres", "lyraeweed", "hiporganophosphates", "borasetanipathogenetics", "volkhabbeedrones", 
        "wulpahyperboresystems", "motronaexperiencejelly", "lucanonionhead", "tanmarktranquiltea", "onionhead", "tarachspice", "masterchefs", "xihebiomorphiccompanions", "mulachigiantfungus", 
        "tiolcewaste2pasteunits", "neritusberries", "chieridanimarinepaste", "ltthypersweet", "medbstarlube", "alyabodysoap", "galactictravelguide", "cromsilverfesh", "duradrives", 
        "alacarakmoskinart", "rajukrumultistoves", "cetirabbits", "aepyornisegg", "ngunamodernantiques", "mokojingbeastfeast", "thewatersofshintara", "ultracompactprocessorprototypes", 
        "kachiriginfilterleeches", "utgaroarmillennialeggs", "helvetitjpearls", "ceremonialheiketea", "vidavantianlace", "bakedgreebles", "harmasilversearum", "noneuclidianexotanks", 
        "jaradharrepuzzlebox", "coquimspongiformvictuals", "onionheadbetastrain", "albinoquechuamammothmeat", "karetiicouture", "platinumalloy", "korokungpellets", "aroucaconventualsweets", 
        "kamorinhistoricweapons", "belalansrayleather", "mukusubiichitinos", "cd75kittenbrandcoffee", "shanscharisorchid", "vanayequiceratomorphafur", "eleuthermals", "apavietii", 
        "deuringastruffles", "hip118311swarm", "giantverrix", "azuremilk", "leestianeviljuice", "disomacorn", "uszaiantreegrub", "baltahsinevacuumkrill", "lavianbrandy", "orrerianviciousbrew",
        "leatheryeggs", "anynacoffee", "deltaphoenicispalms", "personalgifts", "edenapplesofaerial", "hr7221wheat", "yasokondileaf", "holvaduellingblades", "anduligafireworks", "burnhambiledistillate", 
        "kinagoviolins", "ngadandarifireopals", "rapabaosnakeskins", "toxandjivirocide", "kamitracigars", "wuthielokufroth", "sanumadecorativemeat", "geawendancedust", "jarouarice", "giantirukamasnails", 
        "classifiedexperimentalequipment", "njangarisaddles", "soontillrelics", "gomanyauponcoffee", "karsukilocusts", "eshuumbrellas", "wheemetewheatcakes", 
        "jaquesquinentianstill", "tianveganmeat", "sothiscrystallinegold", "sothiscrystallinesilver", "sothiscrystallinelithium"}

    salvage_types = {"occupiedcryopod", "damagedescapepod", "wreckagecomponents", "usscargoblackbox"}

    wake_scan_materials_names = {"disruptedwakeechoes", "wakesolutions", "fsdtelemetry", "hyperspacetrajectories", "dataminedwake"}

    donation_missions = r"^Mission_Altruism.*$"

    HISTORY_DEPTH: int = 20 #increased to 20 from 10 for the multiple cartography merits

    def __init__(self) -> None:
        self.__journal_entries_log: list = []
        self.__on_foot: bool = False

    def add_entry(self, entry: dict) -> bool:
        event_type = entry.get("event", "").lower()

        # On foot state handling
        if event_type == "supercruiseentry":
            self.__on_foot = False
        if event_type == "disembark" and bool(entry.get("OnPlanet")) is True:
            self.__on_foot = True
        if event_type == "embark":
            self.__on_foot = False

        # Skip duplicate powerplaymerits with same TotalMerits as last one,
        # and remove the matching entry from the log if found
        if event_type == "powerplaymerits":
            for i, prev_entry in enumerate(self.__journal_entries_log):
                if prev_entry.get("event", "").lower() == "powerplaymerits":
                    if entry.get("TotalMerits") == prev_entry.get("TotalMerits"):
                        # Remove the matching entry from the log
                        #del self.__journal_entries_log[i]
                        return False # Skip this entry
                    break  # Only compare with the most recent previous powerplaymerits

        if event_type not in self.noise:
            self.__journal_entries_log.insert(0, entry)
        else:
            return False
        # Keep only the last HISTORY_DEPTH entries
        if len(self.__journal_entries_log) > self.HISTORY_DEPTH:
            self.__journal_entries_log.pop()
        return True

    # On foot entries are not recorded in the journal currently so the best we can do is group them together
    @property
    def isOnFoot(self) -> bool:
        #logger.debug(f"IsOnFoot: {self.__on_foot}")
        return self.__on_foot

    @property
    def isScan(self) -> bool:
        return self.isShipScan or self.isWakeScan
    
    @property
    def isShipScan(self) -> bool:
        #{ "timestamp":"2025-05-30T20:02:05Z", "event":"ShipTargeted", "TargetLocked":true, "Ship":"viper_mkiv", "Ship_Localised":"Viper Mk IV", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Lehikko;", "PilotName_Localised":"Lehikko", "PilotRank":"Competent", "ShieldHealth":100.000000, "HullHealth":100.000000, "Faction":"Li Yong-Rui", "LegalStatus":"Clean", "Power":"Li Yong-Rui" }
        try:
            #logger.debug(f"iscan recent journal entries: {self.__journal_entries_log}")
            return (((self.__journal_entries_log[1].get("event", "").lower() == "shiptargeted" and self.__journal_entries_log[1].get("ScanStage", 0) >= 2)
                or (self.__journal_entries_log[2].get("event", "").lower() == "shiptargeted" and self.__journal_entries_log[2].get("ScanStage", 0) >= 2))
                and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits"
                and int(self.__journal_entries_log[0].get("MeritsGained", 0)) <= 40)
        except IndexError as e:
            return False
    
    @property
    def isWakeScan(self) -> bool:
        #logger.debug(f"isWakeScan recent journal entries: {self.__journal_entries_log}")
        #{"timestamp":"2025-05-17T10:06:26Z","event":"MaterialCollected","Category":"Encoded","Name":"disruptedwakeechoes","Name_Localised":"Atypical Disrupted Wake Echoes","Count":3}
        try:
            return (len(self.__journal_entries_log) > 2 and 
                    ((self.__journal_entries_log[1].get("event", "") == "MaterialCollected" and self.__journal_entries_log[1].get("Name", "") in self.wake_scan_materials_names)
                        or (self.__journal_entries_log[2].get("event", "") == "MaterialCollected" and self.__journal_entries_log[2].get("Name", "") in self.wake_scan_materials_names)
                    and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits"))
        except IndexError as e:
            return False
    
    @property
    def isRivalPowerKills(self) -> bool:
        try:
            #{ "timestamp":"2025-05-30T20:02:33Z", "event":"ShipTargeted", "TargetLocked":false }
            return (((self.__journal_entries_log[1].get("event", "").lower() == "shiptargeted" and not bool(self.__journal_entries_log[1].get("TargetLocked","true")))
                     or (self.__journal_entries_log[2].get("event", "").lower() == "shiptargeted" and not bool(self.__journal_entries_log[2].get("TargetLocked","true"))))
                and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits")
        except IndexError as e:
            return False

    @property
    def isBounty(self) -> bool:
        #logger.debug(f"isbounty recent journal entries: {self.__journal_entries_log}")
        try:
            if len(self.__journal_entries_log) < 2:
                return False
            # First entry must be powerplaymerits
            if self.__journal_entries_log[0].get("event", "").lower() != "powerplaymerits":
                return False
            # Allow skipping a single additional powerplaymerits event after the first, a second might be a weekly mission completion
            # also skip shiptargeted events
            skipped_merits = False
            for entry in self.__journal_entries_log[1:]:
                event = entry.get("event", "").lower()
                if event == "shiptargeted":
                    continue
                if event == "powerplaymerits" and not skipped_merits:
                    skipped_merits = True
                    continue
                if event == "bounty":
                    return True
                # If we hit any other event before bounty, stop searching
                break
            return False
        except IndexError:
            return False

    @property
    def isPowerPlayDelivery(self) -> bool:
        #logger.debug(f"isPowerPlayDelivery recent journal entries: {self.__journal_entries_log}")
        try:
            if len(self.__journal_entries_log) < 3:
                return False
            else:
                return ((self.__journal_entries_log[1].get("event", "").lower() == "powerplaydeliver" 
                        or self.__journal_entries_log[2].get("event", "").lower() == "powerplaydeliver")
                        and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits")
        except IndexError as e:
            return False
    
    #Donation missions are usually retrospective and are not recorded in the journal until the mission is completed.
    @property
    def isDonationMissionMeritsSecond(self) -> bool:

        try:
            if len(self.__journal_entries_log) < 2:
                return False
            else:
                #Depending on server load powerplay merits events can come before mission completed or vice versa
                return (self.__journal_entries_log[0].get("event", "").lower() == "missioncompleted" 
                        and re.match(self.donation_missions, self.__journal_entries_log[0].get("Name", ""))
                        and self.__journal_entries_log[1].get("event", "").lower() == "powerplaymerits")
        except IndexError as e:
            return False
                   
    @property
    def isDonationMissionMeritsFirst(self) -> bool:
        try:
            if len(self.__journal_entries_log) < 2:
                return False
            else:
                return (self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits"
                            and self.__journal_entries_log[1].get("event", "").lower() == "missioncompleted"
                            and re.match(self.donation_missions, self.__journal_entries_log[1].get("Name", "")))
        except IndexError as e:
            return False

    @property
    def isScanDataLinks(self) -> bool:
        #logger.debug(f"isScanDataLinks recent journal entries: {self.__journal_entries_log}")
        try:
            return (len(self.__journal_entries_log) > 2 and 
                    ((self.__journal_entries_log[1].get("event", "") == "DataScanned" and self.__journal_entries_log[1].get("Type", "") == "$Datascan_ShipUplink;")
                        or (self.__journal_entries_log[2].get("event", "") == "DataScanned" and self.__journal_entries_log[2].get("Type", "") == "$Datascan_ShipUplink;"))
                    and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits")
        except IndexError as e:
            return False
        
    @property
    def isHoloscreenHack(self) -> bool:
        #logger.debug(f"isHoloscreenHack recent journal entries: {self.__journal_entries_log}")
        try:
            return (len(self.__journal_entries_log) > 2 and 
                    ((self.__journal_entries_log[1].get("event", "") == "HoloscreenHacked"
                        or self.__journal_entries_log[2].get("event", "") == "HoloscreenHacked")
                    and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits"))
        except IndexError as e:
            return False

    @property
    def isRareGoods(self) -> bool:
        #logger.debug(f"isRareGoods recent journal entries: {self.__journal_entries_log}")
        try:
            return (len(self.__journal_entries_log) > 2 and 
                    ((self.__journal_entries_log[1].get("event", "") == "MarketSell" and self.__journal_entries_log[1].get("Type", "") in self.rare_goods)
                        or (self.__journal_entries_log[2].get("event", "") == "MarketSell" and self.__journal_entries_log[2].get("Type", "") in self.rare_goods)
                    and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits"))
        except IndexError as e:
            return False
        
    @property
    def isSalvage(self) -> bool:
        #logger.debug(f"isSalvage recent journal entries: {self.__journal_entries_log}")
        try:
            return (len(self.__journal_entries_log) > 2 and 
                    ((self.__journal_entries_log[1].get("event", "") == "SearchAndRescue" and self.__journal_entries_log[1].get("Name", "") in self.salvage_types)
                        or (self.__journal_entries_log[2].get("event", "") == "SearchAndRescue" and self.__journal_entries_log[2].get("Name", "") in self.salvage_types)
                    and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits"))
        except IndexError as e:
            return False
        
    @property
    def isSingleCartography(self) -> bool:
        #logger.debug(f"isCartography recent journal entries: {self.__journal_entries_log}")
        #or self.__journal_entries_log[1].get("event", "") == "MultiSellExplorationData"
        try:
            return (len(self.__journal_entries_log) > 2 and 
                    ((self.__journal_entries_log[1].get("event", "") == "SellExplorationData")
                    or (self.__journal_entries_log[2].get("event", "") == "SellExplorationData")
                    and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits"))
        except IndexError as e:
            return False
        
    @property
    def isHighValueCommditySale(self) -> bool:
        #logger.debug(f"isHighValueCommditySale recent journal entries: {self.__journal_entries_log}")
        try:
            return (len(self.__journal_entries_log) > 2 and 
                (self.__journal_entries_log[1].get("event", "") == "MarketSell" and self.__journal_entries_log[1].get("AvgPricePaid", 0) > 0 and ((self.__journal_entries_log[1].get("SellPrice", 1) / self.__journal_entries_log[1].get("AvgPricePaid", 1)) >= 1.4)
                 or (self.__journal_entries_log[2].get("event", "") == "MarketSell" and self.__journal_entries_log[2].get("AvgPricePaid", 0) > 0 and ((self.__journal_entries_log[2].get("SellPrice", 1) / self.__journal_entries_log[2].get("AvgPricePaid", 1)) >= 1.4)
                and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits")))
        except IndexError as e:
            return False
        
    @property
    def isLowValueCommditySale(self) -> bool:
        #logger.debug(f"isLowValueCommditySale recent journal entries: {self.__journal_entries_log}")
        try: 
            return (len(self.__journal_entries_log) > 2 and 
                self.__journal_entries_log[1].get("event", "") == "MarketSell" and self.__journal_entries_log[1].get("SellPrice", 0) <= 500
                and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits")
        except IndexError as e:
            return False
        
    @property
    def isExobiology(self) -> bool:
        #logger.debug(f"isExobiology recent journal entries: {self.__journal_entries_log}")
        try: 
            return (len(self.__journal_entries_log) > 2 and 
                (self.__journal_entries_log[1].get("event", "") == "SellOrganicData"
                 or self.__journal_entries_log[2].get("event", "") == "SellOrganicData")
                and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits")
        except IndexError as e:
            return False
        
    @property
    def isMined(self) -> bool:
        #logger.debug(f"isMined recent journal entries: {self.__journal_entries_log}")
        try: 
            return (len(self.__journal_entries_log) > 2 and
                ((self.__journal_entries_log[1].get("event", "") == "MarketSell" and self.__journal_entries_log[1].get("AvgPricePaid", 0) == 0)
                 or (self.__journal_entries_log[2].get("event", "") == "MarketSell" and self.__journal_entries_log[2].get("AvgPricePaid", 0) == 0))
                and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits")
        except IndexError as e:
            return False
        
    @property
    def isCommitCrimes(self) -> bool:
        #logger.debug(f"isCommitCrimes recent journal entries: {self.__journal_entries_log}")
        #{"timestamp":"2025-05-18T10:02:47Z","event":"PowerplayMerits","Power":"Jerome Archer","MeritsGained":268,"TotalMerits":1205795}
        #{"timestamp":"2025-05-18T10:02:47Z","event":"CommitCrime","CrimeType":"murder","Faction":"Inara Nexus","Victim":"Mike McClay","Bounty":5000}       
        try: 
            return (len(self.__journal_entries_log) > 2 
                    and (self.__journal_entries_log[1].get("event", "") == "CommitCrime" or self.__journal_entries_log[2].get("event", "") == "CommitCrime")
                    and self.__journal_entries_log[0].get("event", "").lower() == "powerplaymerits")
        except IndexError as e:
            return False
        
    @property
    def entries(self) -> list:
        #logger.debug(f"entries: {self.__journal_entries_log}")
        return self.__journal_entries_log
    
    def get_mined_commodity(self) -> str:
        #logger.debug(f"get_mind_commodity recent journal entries: {self.__journal_entries_log}")
        if len(self.__journal_entries_log) > 2:
            if self.__journal_entries_log[1].get("event", "") == "MarketSell" and self.__journal_entries_log[1].get("AvgPricePaid", 0) == 0:
                return self.__journal_entries_log[1].get("Type", "")
            elif self.__journal_entries_log[2].get("event", "") == "MarketSell" and self.__journal_entries_log[2].get("AvgPricePaid", 0) == 0:
                return self.__journal_entries_log[2].get("Type", "")
        return ""

    def get_mined_tonnage(self) -> int:
        #logger.debug(f"get_mind_commodity recent journal entries: {self.__journal_entries_log}")
        if len(self.__journal_entries_log) > 2:
            if self.__journal_entries_log[1].get("event", "") == "MarketSell" and self.__journal_entries_log[1].get("AvgPricePaid", 0) == 0:
                return self.__journal_entries_log[1].get("Count", 0)
            elif self.__journal_entries_log[2].get("event", "") == "MarketSell" and self.__journal_entries_log[2].get("AvgPricePaid", 0) == 0:
                return self.__journal_entries_log[2].get("Count", 0)
        return 0

    def get_multiple_cartography(self) -> int:
        #logger.debug(f"get_multiple_cartography recent journal entries: {self.__journal_entries_log}")
        return self._get_multi_entries_merits("MultiSellExplorationData")
    
    def _get_multi_entries_merits(self, target_event: str) -> int:
        multiple_target_event = False
        for entry in self.__journal_entries_log:
            if entry.get("event", "").lower() == target_event.lower():
                multiple_target_event = True
                break

        if multiple_target_event:
            """
            Loops through the __journal_entries_log and totals the MeritsGained for consecutive
            'powerplaymerits' events. Skips initial non-'powerplaymerits' events and stops when
            encountering any other event except 'target_event'.
            """
            total_merits = 0
            counting = False  # Flag to start counting once a 'powerplaymerits' event is found
            target_event_found = False  # Flag to check if target_event is found
            log_entry = None

            for log_entry in self.__journal_entries_log:
                event = log_entry.get("event", "").lower()

                if event == "powerplaymerits":
                    counting = True  # Start counting once a 'powerplaymerits' event is found
                    total_merits += log_entry.get("MeritsGained", 0)
                elif event == target_event.lower():
                    #if counting:
                    target_event_found = True
                    continue  # Allow 'target_event' while counting
                elif counting and not target_event_found:
                        total_merits = 0
                        break  # Stop counting if a non-'powerplaymerits' and non-'target_event' event is found
                else:
                    if counting:
                        break  # Stop counting if any other event is found
            return total_merits
        else:
            return 0