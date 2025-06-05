import unittest
from src.rares import Rares, RareExport

class TestRares(unittest.TestCase):
    def setUp(self):
        """
        Set up the test case with a mock Rares instance and known data.
        """
        # Create a Rares instance and mock the cache with known data
        self.rares = Rares()
        self.rares._rares_data_cache = {
            "rare1": [RareExport({
                "commodityName": "rare1",
                "systemX": 0, "systemY": 0, "systemZ": 0,
                "stationName": "Station A"
            })],
            "rare2": [RareExport({
                "commodityName": "rare2",
                "systemX": 3, "systemY": 4, "systemZ": 0,
                "stationName": "Station B"
            })],
            "rare3": [RareExport({
                "commodityName": "rare3",
                "systemX": 10, "systemY": 0, "systemZ": 0,
                "stationName": "Station C"
            })],
            "rare4": []
        }
        self.rares.rare_goods = ["rare1", "rare2", "rare3", "rare4"]

    def test_distance_sorted_rares(self):
        """
        Test that distance_sorted_rares returns rares sorted by distance from a reference point.
        """
        # Reference point at (0, 0, 0)
        sorted_rares = self.rares.distance_sorted_rares(0, 0, 0)
        # Should be sorted by distance: rare1 (0), rare2 (5), rare3 (10)
        self.assertEqual(sorted_rares[0][0], "rare1")
        self.assertEqual(sorted_rares[1][0], "rare2")
        self.assertEqual(sorted_rares[2][0], "rare3")
        self.assertAlmostEqual(sorted_rares[0][2], 0.0)
        self.assertAlmostEqual(sorted_rares[1][2], 5.0)
        self.assertAlmostEqual(sorted_rares[2][2], 10.0)

    def test_distance_sorted_rares_2(self):
        """
        Test that distance_sorted_rares returns rares sorted by distance from a reference point.
        """
        # Reference point at (11, 0, 0)
        sorted_rares = self.rares.distance_sorted_rares(11, 0, 0)
        # Should be sorted by distance: rare1 (0), rare2 (5), rare3 (10)
        self.assertEqual(sorted_rares[0][0], "rare3")
        self.assertEqual(sorted_rares[1][0], "rare2")
        self.assertEqual(sorted_rares[2][0], "rare1")
        #self.assertAlmostEqual(sorted_rares[0][2], 0.0)
        #self.assertAlmostEqual(sorted_rares[1][2], 5.0)
        #self.assertAlmostEqual(sorted_rares[2][2], 10.0)

if __name__ == "__main__":
    unittest.main()