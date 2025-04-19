class Socials:
    """A class to manage social media links for different powers in the game."""
    
    @staticmethod
    def get_links(power_name):
        powers = {
            "A. Lavingny-Duval": {
                "discord": "https://discord.gg/h28SG5H",
                "reddit": "http://www.reddit.com/r/EliteLavigny"
            },
            "Aisling Duval": {
                "discord": "https://discord.gg/5uejtc4",
                "reddit": "http://www.reddit.com/r/AislingDuval"
            },
            "Archon Delane": {
                "discord": "https://discord.gg/K5azNaB",
                "reddit": "http://www.reddit.com/r/KumoCrew"
            },
            "Denton Patreus": {
                "discord": "https://discord.gg/RjWn3qv",
                "reddit": "http://www.reddit.com/r/ElitePatreus"
            },
            "Edmund Mahon": {
                "discord": "https://discord.gg/ekFSxK9meG",
                "reddit": "http://www.reddit.com/r/EliteMahon"
            },
            "Felicia Winters": {
                "discord": "https://discord.gg/8QjHwMF",
                "reddit": "https://www.reddit.com/r/EliteWinters/"
            },
            "Jerome Archer": {
                "discord": "https://discord.gg/8QjHwMF",
                "reddit": "https://www.reddit.com/r/EliteArcher/"
            },
            "Li Yong-Rui": {
                "discord": "https://discord.gg/vQqXK6W96F",
                "reddit": "http://www.reddit.com/r/EliteSirius"
            },
            "Nakato Kaine": {
                "discord": "https://discord.gg/bJEyseAVGx",
                "reddit": "https://www.reddit.com/r/EliteKaine/"
            },
            "Pranav Antal": {
                "discord": "https://discord.com/invite/Ez6jHz4",
                "reddit": "http://www.reddit.com/r/EliteAntal"
            },
            "Yuri Grom": {
                "discord": "https://discord.com/invite/PEUp2zA",
                "reddit": "https://www.reddit.com/r/EliteGrom/"
            },
            "Zemina Torval": {
                "discord": "https://discord.gg/cj2DgwQ",
                "reddit": "http://www.reddit.com/r/EliteTorval"
            }
        }
        return powers.get(power_name, "Power not found.")

# Example usage:
# socials = Socials()
# print(socials.get_links("Aisling Duval"))