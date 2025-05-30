import unittest
from src.socials import Socials

class TestSocials(unittest.TestCase):
    def test_known_power(self):
        links = Socials.get_links("Aisling Duval")
        self.assertIsInstance(links, dict)
        self.assertIn("discord", links)
        self.assertIn("reddit", links)
        self.assertEqual(links["discord"], "https://discord.gg/5uejtc4")
        self.assertEqual(links["reddit"], "http://www.reddit.com/r/AislingDuval")

    def test_unknown_power(self):
        links = Socials.get_links("Unknown Power")
        self.assertTrue(links == "")

    def test_jerome_archer_discord(self):
        links = Socials.get_links("Jerome Archer")
        self.assertIn("discord", links)
        self.assertTrue(links["discord"].startswith("discord://") or links["discord"].startswith("https://"))

    def test_all_powers_have_discord_and_reddit(self):
        # List of all powers in the dictionary
        powers = [
            "Arissa Lavigny-Duval", "Aisling Duval", "Archon Delane", "Denton Patreus",
            "Edmund Mahon", "Felicia Winters", "Jerome Archer", "Li Yong-Rui",
            "Nakato Kaine", "Pranav Antal", "Yuri Grom", "Zemina Torval"
        ]
        for power in powers:
            with self.subTest(power=power):
                links = Socials.get_links(power)
                self.assertIsInstance(links, dict)
                self.assertIn("discord", links)
                self.assertIn("reddit", links)

if __name__ == "__main__":
    unittest.main()