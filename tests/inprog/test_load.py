import unittest
from unittest.mock import MagicMock, patch
import sys
#import os
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.load import journal_entry

# Patch sys.modules to mock dependencies from load.py
sys.modules['locale'] = MagicMock()
sys.modules['ppp'] = MagicMock()
sys.modules['logger'] = MagicMock()
sys.modules['SystemProgress'] = MagicMock()
sys.modules['SessionProgress'] = MagicMock()
sys.modules['datetime'] = MagicMock()

# Now import the function under test

class TestJournalEntry(unittest.TestCase):
    def setUp(self):
        # Patch global variables and dependencies
        patcher_locale = patch('locale.setlocale')
        patcher_ppp = patch('load.ppp')
        patcher_logger = patch('load.logger')
        patcher_SystemProgress = patch('load.SystemProgress')
        patcher_SessionProgress = patch('load.SessionProgress')
        patcher_datetime = patch('load.datetime')
        self.addCleanup(patcher_locale.stop)
        self.addCleanup(patcher_ppp.stop)
        self.addCleanup(patcher_logger.stop)
        self.addCleanup(patcher_SystemProgress.stop)
        self.addCleanup(patcher_SessionProgress.stop)
        self.addCleanup(patcher_datetime.stop)
        self.mock_locale = patcher_locale.start()
        self.mock_ppp = patcher_ppp.start()
        self.mock_logger = patcher_logger.start()
        self.mock_SystemProgress = patcher_SystemProgress.start()
        self.mock_SessionProgress = patcher_SessionProgress.start()
        self.mock_datetime = patcher_datetime.start()

        # Setup ppp mock structure
        self.mock_ppp.recent_journal_log.add_entry = MagicMock()
        self.mock_ppp.recent_journal_log.get_multiple_cartography = MagicMock(return_value=0)
        self.mock_ppp.recent_journal_log.isScan = False
        self.mock_ppp.recent_journal_log.isBounty = False
        self.mock_ppp.recent_journal_log.isPowerPlayDelivery = False
        self.mock_ppp.recent_journal_log.isDonationMissionMeritsFirst = False
        self.mock_ppp.recent_journal_log.isDonationMissionMeritsSecond = False
        self.mock_ppp.recent_journal_log.isScanDataLinks = False
        self.mock_ppp.recent_journal_log.isHoloscreenHack = False
        self.mock_ppp.recent_journal_log.isRareGoods = False
        self.mock_ppp.recent_journal_log.isSalvage = False
        self.mock_ppp.recent_journal_log.isSingleCartography = False
        self.mock_ppp.recent_journal_log.isHighValueCommditySale = False
        self.mock_ppp.recent_journal_log.isLowValueCommditySale = False
        self.mock_ppp.recent_journal_log.isExobiology = False
        self.mock_ppp.recent_journal_log.isMined = False
        self.mock_ppp.recent_journal_log.isOnFoot = False
        self.mock_ppp.recent_journal_log.get_mined_commodity = MagicMock(return_value=None)
        self.mock_ppp.recent_journal_log.get_mined_tonnage = MagicMock(return_value=None)
        self.mock_ppp.recent_journal_log.isDonationMission = False
        self.mock_ppp.systems = []
        self.mock_ppp.current_system = MagicMock()
        self.mock_ppp.current_session = MagicMock()
        self.mock_ppp.previous_session = MagicMock()
        self.mock_ppp.total_merits = 0
        self.mock_ppp.starting_merits = 0
        self.mock_ppp.last_merits_gained = 0
        self.mock_ppp.Update_Ppp_Display = MagicMock()
        self.mock_ppp.CurrentRank = MagicMock(return_value=1)

        # Setup activities mock
        self.mock_ppp.current_session.activities = MagicMock()
        self.mock_ppp.current_session.earned_merits = 0
        self.mock_ppp.current_session.power_play = ''
        self.mock_ppp.current_session.power_play_rank = 0
        self.mock_ppp.current_session.commodities = []
        self.mock_ppp.current_session.commodities_delivered_systems = []
        self.mock_ppp.current_session.commodities_delivered_types = []
        self.mock_ppp.current_session.time = None

        # Patch global variable
        global wait_for_multi_sell_carto_data
        wait_for_multi_sell_carto_data = -1

    def test_location_event_adds_new_system(self):
        entry = {
            "event": "Location",
            "ControllingPower": "Denton Patreus",
            "PowerplayState": "Fortified",
            "PowerplayStateControlProgress": 0.1,
            "PowerplayStateReinforcement": 100,
            "PowerplayStateUndermining": 10
        }
        system = "TestSystem"
        self.mock_ppp.systems = []
        journal_entry("cmdr", False, system, "station", entry, {})
        self.assertTrue(any(sys.system == system for sys in self.mock_ppp.systems))

    def test_fsdjump_event_adds_new_system(self):
        entry = {
            "event": "FSDJump",
            "ControllingPower": "Yuri Grom",
            "PowerplayState": "Fortified",
            "PowerplayStateControlProgress": 0.2,
            "PowerplayStateReinforcement": 200,
            "PowerplayStateUndermining": 20
        }
        system = "JumpSystem"
        self.mock_ppp.systems = []
        journal_entry("cmdr", False, system, "station", entry, {})
        self.assertTrue(any(sys.system == system for sys in self.mock_ppp.systems))

    def test_docked_event_starts_new_session(self):
        entry = {"event": "Docked"}
        old_session = MagicMock()
        self.mock_ppp.current_session = old_session
        journal_entry("cmdr", False, "sys", "station", entry, {})
        self.assertNotEqual(self.mock_ppp.current_session, old_session)

    def test_powerplaycollect_adds_commodity(self):
        entry = {
            "event": "PowerplayCollect",
            "Type": "republicanfieldsupplies",
            "Type_Localised": "Archer's Field Supplies",
            "Count": 5
        }
        system = "CollectSystem"
        self.mock_ppp.current_session.add_commodity = MagicMock()
        journal_entry("cmdr", False, system, "station", entry, {})
        self.mock_ppp.current_session.add_commodity.assert_called()

    def test_powerplaydeliver_adds_commodity(self):
        entry = {
            "event": "PowerplayDeliver",
            "Type": "republicanfieldsupplies",
            "Type_Localised": "Archer's Field Supplies",
            "Count": 5
        }
        system = "DeliverSystem"
        self.mock_ppp.current_session.add_commodity = MagicMock()
        journal_entry("cmdr", False, system, "station", entry, {})
        self.mock_ppp.current_session.add_commodity.assert_called()

    def test_deliverpowermicroresources_adds_commodity(self):
        entry = {
            "event": "DeliverPowerMicroResources",
            "MicroResources": [
                {"Name": "powerpropagandadata", "Name_Localised": "Power Political Data", "Count": 1}
            ]
        }
        system = "MicroSystem"
        self.mock_ppp.current_session.add_commodity = MagicMock()
        journal_entry("cmdr", False, system, "station", entry, {})
        self.mock_ppp.current_session.add_commodity.assert_called()

    def test_powerplaymerits_assigns_merits(self):
        entry = {
            "event": "PowerplayMerits",
            "Power": "Jerome Archer",
            "MeritsGained": 10,
            "TotalMerits": 100
        }
        system = "MeritSystem"
        self.mock_ppp.systems = []
        self.mock_ppp.current_session.activities.add_unknown_merits = MagicMock()
        journal_entry("cmdr", False, system, "station", entry, {})
        self.assertEqual(self.mock_ppp.total_merits, 100)
        self.assertTrue(any(sys.system == system for sys in self.mock_ppp.systems))

    def test_powerplayrank_sets_rank(self):
        entry = {
            "event": "PowerplayRank",
            "Rank": 5
        }
        self.mock_ppp.current_session.power_play_rank = 0
        journal_entry("cmdr", False, "sys", "station", entry, {})
        self.assertEqual(self.mock_ppp.current_session.power_play_rank, 5)

    def test_powerplay_sets_power_and_merits(self):
        entry = {
            "event": "Powerplay",
            "Power": "Jerome Archer",
            "Rank": 7,
            "Merits": 1234
        }
        system = "PowerSystem"
        self.mock_ppp.systems = []
        journal_entry("cmdr", False, system, "station", entry, {})
        self.assertEqual(self.mock_ppp.current_session.power_play, "Jerome Archer")
        self.assertEqual(self.mock_ppp.current_session.power_play_rank, 7)
        self.assertEqual(self.mock_ppp.starting_merits, 1234)
        self.assertEqual(self.mock_ppp.total_merits, 1234)
        self.assertTrue(any(sys.system == system for sys in self.mock_ppp.systems))

    def test_missioncompleted_moves_unknown_merits(self):
        entry = {
            "event": "MissionCompleted"
        }
        self.mock_ppp.current_session.activities.get_unknown_merits = MagicMock(return_value=10)
        self.mock_ppp.recent_journal_log.isDonationMissionMeritsSecond = True
        self.mock_ppp.current_session.activities.add_donation_mission_merits = MagicMock()
        self.mock_ppp.current_session.activities.add_unknown_merits = MagicMock()
        self.mock_ppp.last_merits_gained = 10
        journal_entry("cmdr", False, "sys", "station", entry, {})
        self.mock_ppp.current_session.activities.add_donation_mission_merits.assert_called_with(10)
        self.mock_ppp.current_session.activities.add_unknown_merits.assert_called_with(-10)

    def test_multisellexplorationdata_sets_wait(self):
        entry = {"event": "MultiSellExplorationData"}
        global wait_for_multi_sell_carto_data
        wait_for_multi_sell_carto_data = -1
        journal_entry("cmdr", False, "sys", "station", entry, {})
        self.assertEqual(wait_for_multi_sell_carto_data, 5)

if __name__ == "__main__":
    unittest.main()