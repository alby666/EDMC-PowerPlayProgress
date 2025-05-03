from config import appname, config # type: ignore # noqa: N813
from EDMCLogging import get_plugin_logger # type: ignore # noqa: N813
from consts import PLUGIN_NAME # type: ignore # noqa: N813

logger = get_plugin_logger(f"{appname}.{PLUGIN_NAME}")

class SessionProgress(object):
    
    class Activities(object):
        
        class Activity(object):
            def __init__(self, activity_type = '', merits = 0) -> None:
                self.activity_type = activity_type
                self.merits = merits

        class MinedCommodity(object):
            def __init__(self, commodity_type = '', merits = 0, tonnage = 0) -> None:
                self.commodity_type = commodity_type
                self.merits = merits
                self.tonnage = tonnage

        def __init__(self) -> None:
            self.activities_type_list = {0: "Unknown:\t", 1: "Ship Scans:\t", 2: "Bounties:\t", 3: "Powerplay Deliveries:", 4: "Donation Missions:", 5: "Scan Data Links:", 6: "Holoscreen Hacks:"
                                         , 7: "Rare Goods:\t", 8: "Salvage:\t", 9 : "Cartography:\t", 10: "High Value Commodities:", 11: "Low Value Commodities:", 12: "Exobiology:\t", 13: "Mined:\t"}
            self.activities: list[SessionProgress.Activities.Activity] = []
            self.mined_commodities: list[SessionProgress.Activities.MinedCommodity] = []
            for item in self.activities_type_list:
                self.activities.append(SessionProgress.Activities.Activity(self.activities_type_list[item], 0))

        def add_unknown_merits(self, merits) -> int:
            self.activities[0].merits += merits
            return self.activities[0].merits
        
        def get_unknown_merits(self) -> int:
            return self.activities[0].merits

        def add_ship_scan_merits(self, merits) -> int:
            self.activities[1].merits += merits
            return self.activities[1].merits
        
        def add_bounty_merits(self, merits) -> int:
            self.activities[2].merits += merits
            return self.activities[2].merits
        
        def add_powerplay_delivery_merits(self, merits) -> int:
            self.activities[3].merits += merits
            return self.activities[3].merits
        
        def add_donation_mission_merits(self, merits) -> int:
            self.activities[4].merits += merits
            return self.activities[4].merits
        
        def add_scan_data_links_merits(self, merits) -> int:
            self.activities[5].merits += merits
            return self.activities[5].merits

        def add_holoscreen_hacks_merits(self, merits) -> int:
            self.activities[6].merits += merits
            return self.activities[6].merits
        
        def add_rare_goods_merits(self, merits) -> int:
            self.activities[7].merits += merits
            return self.activities[7].merits

        def add_salvage_merits(self, merits) -> int:
            self.activities[8].merits += merits
            return self.activities[8].merits
        
        def add_cartography_merits(self, merits) -> int:
            self.activities[9].merits += merits
            return self.activities[9].merits
        
        def add_high_value_commodities_merits(self, merits) -> int:
            self.activities[10].merits += merits
            return self.activities[10].merits
        
        def add_low_value_commodities_merits(self, merits) -> int:
            self.activities[11].merits += merits
            return self.activities[11].merits
        
        def add_exobiology_merits(self, merits) -> int:
            self.activities[12].merits += merits
            return self.activities[12].merits
        
        def add_mined_merits(self, merits, commodity_type, tonnage) -> int:
            found = False
            for item in self.mined_commodities:
                if item.commodity_type == commodity_type:
                    item.merits += merits
                    item.tonnage += tonnage
                    found = True
                    break
            if not found:
                # If the commodity is not found, append it to the list
                self.mined_commodities.append(SessionProgress.Activities.MinedCommodity(commodity_type, merits, tonnage))
                logger.debug(f"Commodity mined: {commodity_type}")
            self.activities[13].merits += merits
            return self.activities[13].merits
        
        def get_total_merits(self) -> int:
            total = 0
            for activity in self.activities:
                total += activity.merits
            return total

    class Commodities(object):
        """
        Represents the commodities collected and delivered in a single session.
        By type and delivered system.
        """
        def __init__(self, type='', type_localised='', delivered_system='', collected=0, delivered=0) -> None:
            self.type = type
            self.type_localised = type_localised
            self.delivered_system = delivered_system
            self.collected = int(collected)
            self.delivered = int(delivered)
    
    """
    Represents the progress in a single session i.e. from the last dock to the current dock or death.
    Except (!!!) for power_ply, powerplay_rank, commodities, commodities_delivered_systems, commodities_delivered_types & activities
    In other words needs refactoring 
    """
    def __init__(self, earned_merits=0, time=0, 
                 is_docking_event=0, power_play_rank=0, power_play='') -> None:
        self.earned_merits = int(earned_merits)
        self.time = int(time)
        self.is_docking_event = int(is_docking_event)
        self.power_play_rank = int(power_play_rank)
        self.power_play = power_play
        self.commodities: list[SessionProgress.Commodities] = []
        self.commodities_delivered_systems: list[str] = []
        self.commodities_delivered_types: list[str] = []
        self.activities: SessionProgress.Activities = SessionProgress.Activities()

    @property
    def total_commodities_collected(self):
        total = 0
        for c in self.commodities:
            total += c.collected
        return total

    @property
    def total_commodities_delivered(self):
        total = 0
        for c in self.commodities:
            total += c.delivered
        return total

    def total_commodities_delivered_by_system(self, delivered_system: str):
        total = 0
        for c in self.commodities:
            if c.delivered_system == delivered_system:
                total += c.delivered
        return total

    def total_commodities_delivered_by_type(self, type_localised: str):
        total = 0
        for c in self.commodities:
            if c.type_localised == type_localised:
                total += c.delivered
        return total

    def add_commodity(self, commodity: Commodities) -> None:
        """
        Add a commodity to the session.
        """
        found = False
        for c in self.commodities:
            if c.type == commodity.type and c.delivered_system == commodity.delivered_system:
                # If the commodity is found, update the collected and delivered values
                c.collected += commodity.collected
                c.delivered += commodity.delivered
                found = True
                break
        if not found:
            # If the commodity is not found, append it to the list
            self.commodities.append(commodity)

        if commodity.delivered > 0:
            # If the commodity is collected, append it to the list
            found = False
            for sys in self.commodities_delivered_systems:
                if sys == commodity.delivered_system:
                    found = True
                    break
            if not found:
                # If the commodity is not found, append it to the list
                self.commodities_delivered_systems.append(commodity.delivered_system)
                logger.debug(f"Commodity delivered system: {commodity.delivered_system}")

            found = False
            for typ in self.commodities_delivered_types:
                if typ == commodity.type_localised:
                    found = True
                    break
            if not found:
                # If the commodity is not found, append it to the list
                self.commodities_delivered_types.append(commodity.type_localised)
                logger.debug(f"Commodity delivered type: {commodity.type_localised}")