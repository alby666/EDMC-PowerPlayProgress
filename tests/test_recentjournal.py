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

if __name__ == "__main__":
    unittest.main()