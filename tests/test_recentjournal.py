import unittest
from src.recentjournal import RecentJournal

class TestRecentJournal(unittest.TestCase):
    def setUp(self):
        """
        Set up a new RecentJournal instance before each test.
        """
        self.recent_journal = RecentJournal()
        self.recent_journal.add_entry({"timestamp":"2025-05-09T21:06:04Z","event":"Docked","StationName":"Hardwick Hub","StationType":"Coriolis","Taxi":False,"Multicrew":False,"StarSystem":"Nihursaga","SystemAddress":2999791389027,"MarketID":3228194304,"StationFaction":{"Name":"Nihursaga Coalition"},"StationGovernment":"$government_Confederacy;","StationGovernment_Localised":"Confederacy","StationAllegiance":"Federation","StationServices":["dock","autodock","blackmarket","commodities","contacts","exploration","missions","outfitting","crewlounge","rearm","refuel","repair","shipyard","tuning","engineer","missionsgenerated","flightcontroller","stationoperations","powerplay","searchrescue","stationMenu","shop","livery","socialspace","bartender","vistagenomics","pioneersupplies","apexinterstellar","frontlinesolutions","registeringcolonisation"],"StationEconomy":"$economy_Industrial;","StationEconomy_Localised":"Industrial","StationEconomies":[{"Name":"$economy_Industrial;","Name_Localised":"Industrial","Proportion":1.0}],"DistFromStarLS":232712.118768,"LandingPads":{"Small":17,"Medium":18,"Large":9}})
        self.recent_journal.add_entry({"timestamp":"2025-05-09T21:07:05Z", "event":"CommunityGoal", "CurrentGoals":[ { "CGID":818, "Title":"Support Winter's Forces in LP 855-34 ", "SystemName":"LP 855-34", "MarketName":"Rhea's Resilience", "Expiry":"2025-05-15T07:00:00Z", "IsComplete":False, "CurrentTotal":4392258, "PlayerContribution":0, "NumContributors":6424, "TopTier":{ "Name":"Tier 6", "Bonus":"" }, "TopRankSize":10, "PlayerInTopRank":False, "TierReached":"Tier 4", "PlayerPercentileBand":100, "Bonus":65000000 } ] })
        self.recent_journal.add_entry({"timestamp":"2025-05-09T21:05:27Z","event":"SupercruiseExit","Taxi":False,"Multicrew":False,"StarSystem":"Nihursaga","SystemAddress":2999791389027,"Body":"Hardwick Hub","BodyID":8,"BodyType":"Station"})
        self.recent_journal.add_entry({"timestamp":"2025-05-09T21:03:58Z","event":"ShipTargeted","TargetLocked":True,"Ship":"independant_trader","Ship_Localised":"Keelback","ScanStage":0})

    def test_add_entry(self):
        """
        Test adding an entry to the journal.
        CommunityGoal would be filtered out as noise in teh recent journal
        """
        entry = {"event": "PowerplayMerits", "MeritsGained": 10}
        self.recent_journal.add_entry(entry)
        self.assertEqual(len(self.recent_journal._RecentJournal__journal_entries_log), 4)
        self.assertEqual(self.recent_journal._RecentJournal__journal_entries_log[0], entry)

    def test_is_on_foot(self):
        """
        Test the isOnFoot property.
        """
        self.recent_journal.add_entry({"event": "Disembark", "OnPlanet": True})
        self.assertTrue(self.recent_journal.isOnFoot)

        self.recent_journal.add_entry({"event": "Embark"})
        self.assertFalse(self.recent_journal.isOnFoot)

    def test_is_bounty(self):
        """
        Test the isBounty property.
        """        
        self.recent_journal.add_entry({"event": "Bounty"})
        self.recent_journal.add_entry({"event": "PowerplayMerits"})
        self.assertTrue(self.recent_journal.isBounty)

    def test_is_powerplay_delivery(self):
        """
        Test the isPowerPlayDelivery property.
        """
        self.recent_journal.add_entry({"event": "PowerplayDeliver"})
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:20Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168253 })
        self.assertTrue(self.recent_journal.isPowerPlayDelivery)

    def test_get_multiple_cartography(self):
        """
        Test the get_multiple_cartography method.
        """
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:20Z", "event":"MultiSellExplorationData", "Discovered":[ { "SystemName":"HIP 37528", "NumBodies":1 }, { "SystemName":"Antliae Sector XU-P b5-0", "NumBodies":1 }, { "SystemName":"Col 285 Sector YY-F b12-0", "NumBodies":1 }, { "SystemName":"Wregoe ZU-G d10-34", "NumBodies":10 }, { "SystemName":"Col 285 Sector XY-Q c5-10", "NumBodies":4 }, { "SystemName":"Wregoe ZP-N c20-10", "NumBodies":2 }, { "SystemName":"Tibionis", "NumBodies":4 }, { "SystemName":"Wregoe JI-I c23-12", "NumBodies":3 }, { "SystemName":"Wregoe YA-X b56-2", "NumBodies":13 }, { "SystemName":"IC 2602 Sector ZK-V b3-2", "NumBodies":10 }, { "SystemName":"Wregoe XQ-L c21-21", "NumBodies":3 }, { "SystemName":"Wregoe VQ-L c21-22", "NumBodies":9 }, { "SystemName":"Wregoe CN-X b42-3", "NumBodies":2 }, { "SystemName":"Wregoe QG-B c27-27", "NumBodies":4 }, { "SystemName":"Wregoe YQ-L c21-29", "NumBodies":1 }, { "SystemName":"Wregoe JV-H b51-4", "NumBodies":6 }, { "SystemName":"Wregoe ES-X b42-5", "NumBodies":1 }, { "SystemName":"Guroji", "NumBodies":7 }, { "SystemName":"Col 285 Sector MN-O b21-6", "NumBodies":5 }, { "SystemName":"Coalsack Sector UO-Z b6", "NumBodies":1 }, { "SystemName":"Jastreb Sector CB-X b1-7", "NumBodies":3 }, { "SystemName":"IC 2602 Sector JD-Q b6-7", "NumBodies":1 }, { "SystemName":"Coalsack Sector YZ-X b1-8", "NumBodies":1 }, { "SystemName":"Wregoe ZC-N b48-8", "NumBodies":1 } ], "BaseValue":718791, "Bonus":0, "TotalEarnings":718791 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:16Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":13, "TotalMerits":1168216 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":7, "TotalMerits":1168223 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168228 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":10, "TotalMerits":1168238 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168243 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168248 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:20Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168253 })
        self.recent_journal.add_entry({"timestamp":"2025-05-09T21:03:58Z","event":"ShipTargeted","TargetLocked":True,"Ship":"independant_trader","Ship_Localised":"Keelback","ScanStage":0})
        self.assertEqual(self.recent_journal.get_multiple_cartography(), 50)

    def test_get_multiple_cartography2(self):
        """
        Test the get_multiple_cartography method.
        """
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:16Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":13, "TotalMerits":1168216 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":7, "TotalMerits":1168223 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168228 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":10, "TotalMerits":1168238 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168243 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:20Z", "event":"MultiSellExplorationData", "Discovered":[ { "SystemName":"HIP 37528", "NumBodies":1 }, { "SystemName":"Antliae Sector XU-P b5-0", "NumBodies":1 }, { "SystemName":"Col 285 Sector YY-F b12-0", "NumBodies":1 }, { "SystemName":"Wregoe ZU-G d10-34", "NumBodies":10 }, { "SystemName":"Col 285 Sector XY-Q c5-10", "NumBodies":4 }, { "SystemName":"Wregoe ZP-N c20-10", "NumBodies":2 }, { "SystemName":"Tibionis", "NumBodies":4 }, { "SystemName":"Wregoe JI-I c23-12", "NumBodies":3 }, { "SystemName":"Wregoe YA-X b56-2", "NumBodies":13 }, { "SystemName":"IC 2602 Sector ZK-V b3-2", "NumBodies":10 }, { "SystemName":"Wregoe XQ-L c21-21", "NumBodies":3 }, { "SystemName":"Wregoe VQ-L c21-22", "NumBodies":9 }, { "SystemName":"Wregoe CN-X b42-3", "NumBodies":2 }, { "SystemName":"Wregoe QG-B c27-27", "NumBodies":4 }, { "SystemName":"Wregoe YQ-L c21-29", "NumBodies":1 }, { "SystemName":"Wregoe JV-H b51-4", "NumBodies":6 }, { "SystemName":"Wregoe ES-X b42-5", "NumBodies":1 }, { "SystemName":"Guroji", "NumBodies":7 }, { "SystemName":"Col 285 Sector MN-O b21-6", "NumBodies":5 }, { "SystemName":"Coalsack Sector UO-Z b6", "NumBodies":1 }, { "SystemName":"Jastreb Sector CB-X b1-7", "NumBodies":3 }, { "SystemName":"IC 2602 Sector JD-Q b6-7", "NumBodies":1 }, { "SystemName":"Coalsack Sector YZ-X b1-8", "NumBodies":1 }, { "SystemName":"Wregoe ZC-N b48-8", "NumBodies":1 } ], "BaseValue":718791, "Bonus":0, "TotalEarnings":718791 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168248 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:20Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168253 })
        self.recent_journal.add_entry({"timestamp":"2025-05-09T21:03:58Z","event":"ShipTargeted","TargetLocked":True,"Ship":"independant_trader","Ship_Localised":"Keelback","ScanStage":0})
        self.assertEqual(self.recent_journal.get_multiple_cartography(), 50)

    def test_get_multiple_cartography3(self):
        """
        Test the get_multiple_cartography method.
        """
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:16Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":13, "TotalMerits":1168216 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":7, "TotalMerits":1168223 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:20Z", "event":"MultiSellExplorationData", "Discovered":[ { "SystemName":"HIP 37528", "NumBodies":1 }, { "SystemName":"Antliae Sector XU-P b5-0", "NumBodies":1 }, { "SystemName":"Col 285 Sector YY-F b12-0", "NumBodies":1 }, { "SystemName":"Wregoe ZU-G d10-34", "NumBodies":10 }, { "SystemName":"Col 285 Sector XY-Q c5-10", "NumBodies":4 }, { "SystemName":"Wregoe ZP-N c20-10", "NumBodies":2 }, { "SystemName":"Tibionis", "NumBodies":4 }, { "SystemName":"Wregoe JI-I c23-12", "NumBodies":3 }, { "SystemName":"Wregoe YA-X b56-2", "NumBodies":13 }, { "SystemName":"IC 2602 Sector ZK-V b3-2", "NumBodies":10 }, { "SystemName":"Wregoe XQ-L c21-21", "NumBodies":3 }, { "SystemName":"Wregoe VQ-L c21-22", "NumBodies":9 }, { "SystemName":"Wregoe CN-X b42-3", "NumBodies":2 }, { "SystemName":"Wregoe QG-B c27-27", "NumBodies":4 }, { "SystemName":"Wregoe YQ-L c21-29", "NumBodies":1 }, { "SystemName":"Wregoe JV-H b51-4", "NumBodies":6 }, { "SystemName":"Wregoe ES-X b42-5", "NumBodies":1 }, { "SystemName":"Guroji", "NumBodies":7 }, { "SystemName":"Col 285 Sector MN-O b21-6", "NumBodies":5 }, { "SystemName":"Coalsack Sector UO-Z b6", "NumBodies":1 }, { "SystemName":"Jastreb Sector CB-X b1-7", "NumBodies":3 }, { "SystemName":"IC 2602 Sector JD-Q b6-7", "NumBodies":1 }, { "SystemName":"Coalsack Sector YZ-X b1-8", "NumBodies":1 }, { "SystemName":"Wregoe ZC-N b48-8", "NumBodies":1 } ], "BaseValue":718791, "Bonus":0, "TotalEarnings":718791 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168228 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":10, "TotalMerits":1168238 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168243 })
        self.recent_journal.add_entry({"timestamp":"2025-05-09T21:03:58Z","event":"ShipTargeted","TargetLocked":True,"Ship":"independant_trader","Ship_Localised":"Keelback","ScanStage":0})
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:19Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168248 })
        self.recent_journal.add_entry({ "timestamp":"2025-05-09T21:07:20Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":5, "TotalMerits":1168253 })
        self.assertEqual(self.recent_journal.get_multiple_cartography(), 0)

    def test_get_multiple_cartography4(self):
        """
        Test the get_multiple_cartography method again.
        """
        self.recent_journal.add_entry({"timestamp": "2025-05-15T16:55:16Z", "event": "StoredModules", "MarketID": 3226474496, "StationName": "Sverdrup Ring", "StarSystem": "Uzumoku"})
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:15Z","event": "Outfitting","MarketID": 3226474496,"StationName": "Sverdrup Ring","StarSystem": "Uzumoku" })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "MultiSellExplorationData","Discovered": [{"SystemName": "Wredguia SY-S e3-18", "NumBodies": 7}, {"SystemName": "Wredguia HW-L c21-0", "NumBodies": 8}, {"SystemName": "Wredguia MD-R c18-2", "NumBodies": 1}, {"SystemName": "Wredguia UP-N c20-2", "NumBodies": 1}, {"SystemName": "Wredguia OJ-P c19-5", "NumBodies": 1}, {"SystemName": "Wredguia YU-G d10-49", "NumBodies": 5}, {"SystemName": "Wredguia NJ-P c19-7", "NumBodies": 4}, {"SystemName": "Col 285 Sector SK-N c7-10", "NumBodies": 15}, {"SystemName": "Col 285 Sector UZ-O c6-10", "NumBodies": 6}, {"SystemName": "Wolf 635", "NumBodies": 5}, {"SystemName": "Wredguia RR-G b38-1", "NumBodies": 5}, {"SystemName": "Wredguia OQ-I b37-1", "NumBodies": 14}, {"SystemName": "Wredguia ES-X b42-1", "NumBodies": 1}, {"SystemName": "Wredguia NT-V b43-1", "NumBodies": 10}, {"SystemName": "Wredguia GM-Z b41-1", "NumBodies": 10}, {"SystemName": "Col 285 Sector IS-T d3-107", "NumBodies": 3}, {"SystemName": "Wredguia BZ-L b35-2", "NumBodies": 35}, {"SystemName": "Wredguia FF-K b36-2", "NumBodies": 1}, {"SystemName": "Wredguia CE-M b35-2", "NumBodies": 3}, {"SystemName": "Wredguia IY-E b39-2", "NumBodies": 5}, {"SystemName": "Wredguia ZF-B b41-2", "NumBodies": 7}, {"SystemName": "Wredguia VZ-T b44-2", "NumBodies": 2}, {"SystemName": "Wredguia EB-S b45-2", "NumBodies": 1}, {"SystemName": "LHS 3197", "NumBodies": 1}, {"SystemName": "Col 285 Sector OE-P c6-25", "NumBodies": 1}, {"SystemName": "Wredguia TL-I b37-3", "NumBodies": 6}, {"SystemName": "Wredguia RZ-C b40-3", "NumBodies": 3}, {"SystemName": "Col 285 Sector RQ-A b15-3", "NumBodies": 2}, {"SystemName": "Col 285 Sector RW-H b11-4", "NumBodies": 5}, {"SystemName": "Col 285 Sector GT-F b12-5", "NumBodies": 1}, {"SystemName": "Cephei Sector PD-T b3-8", "NumBodies": 8}],"BaseValue": 765503,"Bonus": 0,"TotalEarnings": 765503 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 2,"TotalMerits": 1176323 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 5,"TotalMerits": 1176326 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 5,"TotalMerits": 1176321 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 5,"TotalMerits": 1176316 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 13,"TotalMerits": 1176311 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 7,"TotalMerits": 1176298 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 2,"TotalMerits": 1176291 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:10Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 18,"TotalMerits": 1176289 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:10Z","event": "Docked","StationName": "Sverdrup Ring","StationType": "Coriolis","Taxi": False,"Multicrew": False,"StarSystem": "Uzumoku","SystemAddress": 3308995479907,"MarketID": 3226474496,"StationFaction": { "Name": "Order of Enblackenment","FactionState": "Expansion" },"StationGovernment": "$government_Theocracy;","StationGovernment_Localised": "Theocracy","StationServices": ["dock", "autodock", "commodities", "contacts", "exploration", "missions", "outfitting", "crewlounge", "rearm", "refuel", "repair", "shipyard", "tuning", "engineer", "missionsgenerated", "flightcontroller", "stationoperations", "powerplay", "searchrescue", "materialtrader", "stationMenu", "shop", "livery", "socialspace", "bartender", "vistagenomics", "pioneersupplies", "apexinterstellar", "frontlinesolutions", "registeringcolonisation"],"StationEconomy": "$economy_HighTech;","StationEconomy_Localised": "High Tech","StationEconomies": [{"Name": "$economy_HighTech;", "Name_Localised": "High Tech", "Proportion": 0.8}, {"Name": "$economy_Refinery;", "Name_Localised": "Refinery", "Proportion": 0.2}],"DistFromStarLS": 505443.694744,"LandingPads": { "Small": 5,"Medium": 11,"Large": 6 } })
        self.assertEqual(self.recent_journal._get_multi_entries_merits("MultiSellExplorationData"), 57)

    def test_get_multiple_cartography5(self):
        """
        Test the get_multiple_cartography method again again.
        """
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:10Z","event": "Docked","StationName": "Sverdrup Ring","StationType": "Coriolis","Taxi": False,"Multicrew": False,"StarSystem": "Uzumoku","SystemAddress": 3308995479907,"MarketID": 3226474496,"StationFaction": { "Name": "Order of Enblackenment","FactionState": "Expansion" },"StationGovernment": "$government_Theocracy;","StationGovernment_Localised": "Theocracy","StationServices": ["dock", "autodock", "commodities", "contacts", "exploration", "missions", "outfitting", "crewlounge", "rearm", "refuel", "repair", "shipyard", "tuning", "engineer", "missionsgenerated", "flightcontroller", "stationoperations", "powerplay", "searchrescue", "materialtrader", "stationMenu", "shop", "livery", "socialspace", "bartender", "vistagenomics", "pioneersupplies", "apexinterstellar", "frontlinesolutions", "registeringcolonisation"],"StationEconomy": "$economy_HighTech;","StationEconomy_Localised": "High Tech","StationEconomies": [{"Name": "$economy_HighTech;", "Name_Localised": "High Tech", "Proportion": 0.8}, {"Name": "$economy_Refinery;", "Name_Localised": "Refinery", "Proportion": 0.2}],"DistFromStarLS": 505443.694744,"LandingPads": { "Small": 5,"Medium": 11,"Large": 6 } })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 13,"TotalMerits": 1176311 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 7,"TotalMerits": 1176298 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 2,"TotalMerits": 1176291 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:10Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 18,"TotalMerits": 1176289 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 2,"TotalMerits": 1176323 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 5,"TotalMerits": 1176326 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 5,"TotalMerits": 1176321 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "PowerplayMerits","Power": "Jerome Archer","MeritsGained": 5,"TotalMerits": 1176316 })
        
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:11Z","event": "MultiSellExplorationData","Discovered": [{"SystemName": "Wredguia SY-S e3-18", "NumBodies": 7}, {"SystemName": "Wredguia HW-L c21-0", "NumBodies": 8}, {"SystemName": "Wredguia MD-R c18-2", "NumBodies": 1}, {"SystemName": "Wredguia UP-N c20-2", "NumBodies": 1}, {"SystemName": "Wredguia OJ-P c19-5", "NumBodies": 1}, {"SystemName": "Wredguia YU-G d10-49", "NumBodies": 5}, {"SystemName": "Wredguia NJ-P c19-7", "NumBodies": 4}, {"SystemName": "Col 285 Sector SK-N c7-10", "NumBodies": 15}, {"SystemName": "Col 285 Sector UZ-O c6-10", "NumBodies": 6}, {"SystemName": "Wolf 635", "NumBodies": 5}, {"SystemName": "Wredguia RR-G b38-1", "NumBodies": 5}, {"SystemName": "Wredguia OQ-I b37-1", "NumBodies": 14}, {"SystemName": "Wredguia ES-X b42-1", "NumBodies": 1}, {"SystemName": "Wredguia NT-V b43-1", "NumBodies": 10}, {"SystemName": "Wredguia GM-Z b41-1", "NumBodies": 10}, {"SystemName": "Col 285 Sector IS-T d3-107", "NumBodies": 3}, {"SystemName": "Wredguia BZ-L b35-2", "NumBodies": 35}, {"SystemName": "Wredguia FF-K b36-2", "NumBodies": 1}, {"SystemName": "Wredguia CE-M b35-2", "NumBodies": 3}, {"SystemName": "Wredguia IY-E b39-2", "NumBodies": 5}, {"SystemName": "Wredguia ZF-B b41-2", "NumBodies": 7}, {"SystemName": "Wredguia VZ-T b44-2", "NumBodies": 2}, {"SystemName": "Wredguia EB-S b45-2", "NumBodies": 1}, {"SystemName": "LHS 3197", "NumBodies": 1}, {"SystemName": "Col 285 Sector OE-P c6-25", "NumBodies": 1}, {"SystemName": "Wredguia TL-I b37-3", "NumBodies": 6}, {"SystemName": "Wredguia RZ-C b40-3", "NumBodies": 3}, {"SystemName": "Col 285 Sector RQ-A b15-3", "NumBodies": 2}, {"SystemName": "Col 285 Sector RW-H b11-4", "NumBodies": 5}, {"SystemName": "Col 285 Sector GT-F b12-5", "NumBodies": 1}, {"SystemName": "Cephei Sector PD-T b3-8", "NumBodies": 8}],"BaseValue": 765503,"Bonus": 0,"TotalEarnings": 765503 })
        self.recent_journal.add_entry({ "timestamp": "2025-05-15T16:55:15Z","event": "Outfitting","MarketID": 3226474496,"StationName": "Sverdrup Ring","StarSystem": "Uzumoku" })
        self.recent_journal.add_entry({"timestamp": "2025-05-15T16:55:16Z", "event": "StoredModules", "MarketID": 3226474496, "StationName": "Sverdrup Ring", "StarSystem": "Uzumoku"})
        self.assertEqual(self.recent_journal._get_multi_entries_merits("MultiSellExplorationData"), 57)


    def test_is_mined(self):
        """
        Test the isMined property.
        """
        self.recent_journal.add_entry({"event": "MarketSell", "AvgPricePaid": 0})
        self.recent_journal.add_entry({"timestamp":"2025-05-09T21:06:51Z","event":"PowerplayMerits","Power":"Jerome Archer","MeritsGained":46,"TotalMerits":1168157})
        self.assertTrue(self.recent_journal.isMined)

    def test_get_mined_commodity(self):
        """
        Test the get_mined_commodity method.
        """
        self.recent_journal.add_entry({"event": "MarketSell", "AvgPricePaid": 0, "Type": "Gold"})
        self.recent_journal.add_entry({"timestamp":"2025-05-09T21:06:51Z","event":"PowerplayMerits","Power":"Jerome Archer","MeritsGained":46,"TotalMerits":1168157})
        self.assertEqual(self.recent_journal.get_mined_commodity(), "Gold")

    def test_get_mined_tonnage(self):
        """
        Test the get_mined_tonnage method.
        """
        self.recent_journal.add_entry({"event": "MarketSell", "AvgPricePaid": 0, "Count": 50})
        self.recent_journal.add_entry({"timestamp":"2025-05-09T21:06:51Z","event":"PowerplayMerits","Power":"Jerome Archer","MeritsGained":46,"TotalMerits":1168157})
        self.assertEqual(self.recent_journal.get_mined_tonnage(), 50)

    def test_is_wake_scan(self):
        """
        Test the isWakeScan property.
        """
        self.recent_journal.add_entry({"timestamp":"2025-05-17T10:46:44Z","event":"MaterialCollected","Category":"Encoded","Name":"wakesolutions","Name_Localised":"Strange Wake Solutions","Count":3})
        self.recent_journal.add_entry({"timestamp":"2025-05-17T10:46:45Z","event":"PowerplayMerits","Power":"Jerome Archer","MeritsGained":13,"TotalMerits":1181461})
        self.assertTrue(self.recent_journal.isWakeScan)

    def test_commit_crimes(self):
        """
        Test the commit_crimes method.
        """
        self.recent_journal.add_entry({"timestamp":"2025-05-18T10:02:47Z","event":"CommitCrime","CrimeType":"murder","Faction":"Inara Nexus","Victim":"Mike McClay","Bounty":5000})
        self.recent_journal.add_entry({"timestamp":"2025-05-18T10:02:47Z","event":"PowerplayMerits","Power":"Jerome Archer","MeritsGained":268,"TotalMerits":1205795})
        self.assertTrue(self.recent_journal.isCommitCrimes)

    def test_is_bounty2(self):
        """
        Test the isBounty property.
        """
        self.recent_journal.add_entry({"timestamp":"2025-05-19T19:57:28Z", "event":"Bounty", "Rewards":[ { "Faction":"Inara Nexus", "Reward":372898 } ], "PilotName":"$npc_name_decorate:#name=aigy;", "PilotName_Localised":"aigy", "Target":"krait_mkii", "Target_Localised":"Krait Mk II", "TotalReward":372898, "VictimFaction":"Terra Formations Industries"})
        self.recent_journal.add_entry({"timestamp":"2025-05-19T19:57:28Z", "event":"ShipTargeted", "TargetLocked":False})
        self.recent_journal.add_entry({"timestamp":"2025-05-19T19:57:28Z", "event":"ShipTargeted", "TargetLocked":True, "Ship":"krait_mkii", "Ship_Localised":"Krait Mk II", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Weltschmertz;", "PilotName_Localised":"Weltschmertz", "PilotRank":"Master", "ShieldHealth":64.881157, "HullHealth":100.000000, "Faction":"Terra Formations Industries", "LegalStatus":"Wanted", "Bounty":602879})
        self.recent_journal.add_entry({"timestamp":"2025-05-19T19:57:35Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":91, "TotalMerits":1207320})
        self.assertTrue(self.recent_journal.isBounty)

    def test_is_bounty3(self):
        """
        Test the isBounty property again.
        """
        self.recent_journal.add_entry({"timestamp":"2025-05-30T17:24:33Z","event":"ShipTargeted","TargetLocked":True,"Ship":"cobramkiv","Ship_Localised":"Cobra Mk IV","ScanStage":0})
        self.recent_journal.add_entry({"timestamp":"2025-05-30T17:24:44Z","event":"Bounty","Rewards":[{"Faction":"Daibamba Progressive Party","Reward":193578}],"PilotName":"$npc_name_decorate:#name=James Turner;","PilotName_Localised":"James Turner","Target":"cobramkiv","Target_Localised":"Cobra Mk IV","TotalReward":193578,"VictimFaction":"Daibamba Progressive Party"})
        self.recent_journal.add_entry({"timestamp":"2025-05-30T17:24:45Z","event":"PowerplayMerits","Power":"Jerome Archer","MeritsGained":4800,"TotalMerits":1219057})
        self.recent_journal.add_entry({"timestamp":"2025-05-30T17:24:45Z","event":"PowerplayMerits","Power":"Jerome Archer","MeritsGained":75,"TotalMerits":1219132})
        self.assertTrue(self.recent_journal.isBounty)
        
    def test_is_donation_second(self):
        """
        Test the isDonation property.
        """
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:12Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":42, "TotalMerits":1230328})
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:18Z", "event":"MissionCompleted", "Faction":"League of LHS 197 Order", "Name":"Mission_AltruismCredits_name", "LocalisedName":"Donate 1,000,000 Cr to the cause", "MissionID":1017890050, "Donation":"1000000", "Donated":1000000, "FactionEffects":[ { "Faction":"League of LHS 197 Order", "Effects":[ { "Effect":"$MISSIONUTIL_Interaction_Summary_EP_up;", "Effect_Localised":"The economic status of $#MinorFaction; has improved in the $#System; system.", "Trend":"UpGood" } ], "Influence":[ { "SystemAddress":5068732573073, "Trend":"UpGood", "Influence":"++" } ], "ReputationTrend":"UpGood", "Reputation":"++" } ] })
        self.assertTrue(self.recent_journal.isDonationMissionMeritsSecond)

    def test_is_donation_first(self):
        """
        Test the isDonation property.
        """
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:18Z", "event":"MissionCompleted", "Faction":"League of LHS 197 Order", "Name":"Mission_AltruismCredits_name", "LocalisedName":"Donate 1,000,000 Cr to the cause", "MissionID":1017890050, "Donation":"1000000", "Donated":1000000, "FactionEffects":[ { "Faction":"League of LHS 197 Order", "Effects":[ { "Effect":"$MISSIONUTIL_Interaction_Summary_EP_up;", "Effect_Localised":"The economic status of $#MinorFaction; has improved in the $#System; system.", "Trend":"UpGood" } ], "Influence":[ { "SystemAddress":5068732573073, "Trend":"UpGood", "Influence":"++" } ], "ReputationTrend":"UpGood", "Reputation":"++" } ] })
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:12Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":42, "TotalMerits":1230328})
        self.assertTrue(self.recent_journal.isDonationMissionMeritsFirst)

    def test_is_donation_not_first(self):
        """
        Test the isDonation property.
        """
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:12Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":42, "TotalMerits":1230328})
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:18Z", "event":"MissionCompleted", "Faction":"League of LHS 197 Order", "Name":"Mission_AltruismCredits_name", "LocalisedName":"Donate 1,000,000 Cr to the cause", "MissionID":1017890050, "Donation":"1000000", "Donated":1000000, "FactionEffects":[ { "Faction":"League of LHS 197 Order", "Effects":[ { "Effect":"$MISSIONUTIL_Interaction_Summary_EP_up;", "Effect_Localised":"The economic status of $#MinorFaction; has improved in the $#System; system.", "Trend":"UpGood" } ], "Influence":[ { "SystemAddress":5068732573073, "Trend":"UpGood", "Influence":"++" } ], "ReputationTrend":"UpGood", "Reputation":"++" } ] })
        self.assertFalse(self.recent_journal.isDonationMissionMeritsFirst)

    def test_multiple_donation_missions(self):
        """
        Test the isDonation property.
        """
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:12Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":42, "TotalMerits":1230328 })
        self.assertFalse(self.recent_journal.isDonationMissionMeritsFirst)
        self.assertFalse(self.recent_journal.isDonationMissionMeritsSecond)
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:18Z", "event":"MissionCompleted", "Faction":"League of LHS 197 Order", "Name":"Mission_AltruismCredits_name", "LocalisedName":"Donate 1,000,000 Cr to the cause", "MissionID":1017890050, "Donation":"1000000", "Donated":1000000, "FactionEffects":[ { "Faction":"League of LHS 197 Order", "Effects":[ { "Effect":"$MISSIONUTIL_Interaction_Summary_EP_up;", "Effect_Localised":"The economic status of $#MinorFaction; has improved in the $#System; system.", "Trend":"UpGood" } ], "Influence":[ { "SystemAddress":5068732573073, "Trend":"UpGood", "Influence":"++" } ], "ReputationTrend":"UpGood", "Reputation":"++" } ] })
        self.assertFalse(self.recent_journal.isDonationMissionMeritsFirst)
        self.assertTrue(self.recent_journal.isDonationMissionMeritsSecond)
        self.recent_journal.removeDonationMissionLogs()
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:36Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":42, "TotalMerits":1230370 })
        self.assertFalse(self.recent_journal.isDonationMissionMeritsFirst)
        self.assertFalse(self.recent_journal.isDonationMissionMeritsSecond)
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:36Z", "event":"MissionCompleted", "Faction":"Social Manamaya Democrats", "Name":"Mission_AltruismCredits_name", "LocalisedName":"Donate 1,000,000 Cr to the cause", "MissionID":1017890051, "Donation":"1000000", "Donated":1000000, "FactionEffects":[ { "Faction":"Social Manamaya Democrats", "Effects":[ { "Effect":"$MISSIONUTIL_Interaction_Summary_EP_up;", "Effect_Localised":"The economic status of $#MinorFaction; has improved in the $#System; system.", "Trend":"UpGood" } ], "Influence":[ { "SystemAddress":5068732573073, "Trend":"UpGood", "Influence":"++" } ], "ReputationTrend":"UpGood", "Reputation":"++" } ] })
        self.assertFalse(self.recent_journal.isDonationMissionMeritsFirst)
        self.assertTrue(self.recent_journal.isDonationMissionMeritsSecond)
        self.recent_journal.removeDonationMissionLogs()
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:18Z", "event":"MissionCompleted", "Faction":"League of LHS 197 Order", "Name":"Mission_AltruismCredits_name", "LocalisedName":"Donate 1,000,000 Cr to the cause", "MissionID":1017890050, "Donation":"1000000", "Donated":1000000, "FactionEffects":[ { "Faction":"League of LHS 197 Order", "Effects":[ { "Effect":"$MISSIONUTIL_Interaction_Summary_EP_up;", "Effect_Localised":"The economic status of $#MinorFaction; has improved in the $#System; system.", "Trend":"UpGood" } ], "Influence":[ { "SystemAddress":5068732573073, "Trend":"UpGood", "Influence":"++" } ], "ReputationTrend":"UpGood", "Reputation":"++" } ] })
        self.assertFalse(self.recent_journal.isDonationMissionMeritsFirst)
        self.assertFalse(self.recent_journal.isDonationMissionMeritsSecond)
        self.recent_journal.add_entry({"timestamp":"2025-05-31T14:07:12Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":42, "TotalMerits":1230328 })
        self.assertTrue(self.recent_journal.isDonationMissionMeritsFirst)
        self.assertFalse(self.recent_journal.isDonationMissionMeritsSecond)

    def test_isScan(self):
        """
        Test the isScan property.
        """
        self.recent_journal.add_entry({"timestamp":"2025-06-01T07:58:22Z", "event":"ShipTargeted", "TargetLocked":True, "Ship":"type6", "Ship_Localised":"Type-6 Transporter", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Alexander Lavrov;", "PilotName_Localised":"Alexander Lavrov", "PilotRank":"Harmless", "ShieldHealth":100.000000, "HullHealth":100.000000, "Faction":"Labe State Holdings", "LegalStatus":"Clean" })
        self.recent_journal.add_entry({ "timestamp":"2025-06-01T07:58:22Z", "event":"MaterialCollected", "Category":"Encoded", "Name":"shieldcyclerecordings", "Name_Localised":"Distorted Shield Cycle Recordings", "Count":3 })
        self.recent_journal.add_entry({ "timestamp":"2025-06-01T07:58:22Z", "event":"PowerplayMerits", "Power":"Jerome Archer", "MeritsGained":13, "TotalMerits":1231266 })
        self.assertTrue(self.recent_journal.isScan)

if __name__ == "__main__":
    unittest.main()