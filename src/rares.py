"""
A class to retrieve and process Elite Dangerous rare commdities data
"""
import requests
import math
import asyncio
import aiohttp as aiohttp 
from consts import rare_goods

class RareExport:
    def __init__(self, data: dict):
        self.commodityName = data.get("commodityName")
        self.marketId = data.get("marketId")
        self.stationName = data.get("stationName")
        self.stationType = data.get("stationType")
        self.distanceToArrival = data.get("distanceToArrival")
        self.maxLandingPadSize = data.get("maxLandingPadSize")
        self.bodyId = data.get("bodyId")
        self.bodyName = data.get("bodyName")
        self.systemAddress = data.get("systemAddress")
        self.systemName = data.get("systemName")
        self.systemX = data.get("systemX")
        self.systemY = data.get("systemY")
        self.systemZ = data.get("systemZ")
        self.buyPrice = data.get("buyPrice")
        self.demand = data.get("demand")
        self.demandBracket = data.get("demandBracket")
        self.meanPrice = data.get("meanPrice")
        self.sellPrice = data.get("sellPrice")
        self.stock = data.get("stock")
        self.stockBracket = data.get("stockBracket")
        self.updatedAt = data.get("updatedAt")

class Rares:
    """
    A class to handle rare commodities in Elite Dangerous.
    """

    _rares_data_cache = {}  # Make this a static (class-level) variable

    def __init__(self):
        self.rare_goods = rare_goods

    def is_rare(self, commodity_name: str) -> bool:
        """
        Check if a commodity is considered rare.

        :param commodity_name: The name of the commodity to check.
        :return: True if the commodity is rare, False otherwise.
        """
        return commodity_name.lower() in self.rare_goods

    def get_rares_data(self) -> dict:
        """
        Retrieve export data for each rare commodity from the API, with caching.
        Returns a dictionary mapping commodity names to a list of RareExport instances.
        """
        api_url = "https://api.ardent-insight.com/v2/commodity/name/{}/exports?fleetCarriers=false"
        results = {}
        for commodity in self.rare_goods:
            if commodity in Rares._rares_data_cache:
                results[commodity] = Rares._rares_data_cache[commodity]
                continue
            try:
                url = api_url.format(commodity)
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                # Convert each dict in the response to a RareExport instance
                rare_exports = [RareExport(item) for item in data]
                Rares._rares_data_cache[commodity] = rare_exports
                results[commodity] = rare_exports
            except Exception as e:
                Rares._rares_data_cache[commodity] = {"error": str(e)}
                results[commodity] = {"error": str(e)}
        return results

    async def _fetch_rare(self, session, api_url, commodity):
        url = api_url.format(commodity)
        try:
            async with session.get(url, timeout=10) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return commodity, [RareExport(item) for item in data]
        except Exception as e:
            return commodity, {"error": str(e)}

    async def get_rares_data_async(self):
        api_url = "https://api.ardent-insight.com/v2/commodity/name/{}/exports?fleetCarriers=false"
        results = {}
        async with aiohttp.ClientSession() as session:
            tasks = []
            for commodity in self.rare_goods:
                # Use the rare commodity name if available, otherwise the symbol
                name = self.rare_goods[commodity]["name"] #if isinstance(self.rare_goods[commodity], dict) and "name" in self.rare_goods[commodity] else commodity
                # Check cache by both symbol and name
                if name in Rares._rares_data_cache:  #commodity in Rares._rares_data_cache or 
                    continue
                tasks.append(self._fetch_rare(session, api_url, commodity))
            responses = await asyncio.gather(*tasks)
            for commodity, data in responses:
                name = self.rare_goods[commodity]["name"] #if isinstance(self.rare_goods[commodity], dict) and "name" in self.rare_goods[commodity] else commodity
                Rares._rares_data_cache[name] = data
                results[name] = data
            # Add cached results
            for commodity in self.rare_goods:
                name = self.rare_goods[commodity]["name"] #if isinstance(self.rare_goods[commodity], dict) and "name" in self.rare_goods[commodity] else commodity
                # Prefer cache by name, fallback to symbol
                if name in Rares._rares_data_cache:
                    results[name] = Rares._rares_data_cache[name]
        return results

    def distance_sorted_rares(self, x: float, y: float, z: float) -> list:
        """
        Returns a list of (commodity_name, RareExport, distance) tuples for all rare goods,
        ordered by distance from the given (x, y, z) coordinates (nearest first).
        """
        rares_data = self.get_rares_data()
        rare_distances = []

        for commodity, exports in rares_data.items():
            # Only process if exports is a list (not an error dict)
            if isinstance(exports, list) and exports:
                for export in exports:
                    # Ensure export has systemX, systemY, systemZ
                    if (
                        hasattr(export, "systemX") and export.systemX is not None and
                        hasattr(export, "systemY") and export.systemY is not None and
                        hasattr(export, "systemZ") and export.systemZ is not None
                    ):
                        dx = export.systemX - x
                        dy = export.systemY - y
                        dz = export.systemZ - z
                        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                        rare_distances.append((commodity, export, distance))

        # Sort by distance
        rare_distances.sort(key=lambda tup: tup[2])
        return rare_distances

    async def distance_sorted_rares_async(self, x: float, y: float, z: float) -> list:
        """
        Async version: Returns a list of (commodity_name, RareExport, distance) tuples for all rare goods,
        ordered by distance from the given (x, y, z) coordinates (nearest first).
        """
        rares_data = await self.get_rares_data_async()
        rare_distances = []

        for commodity, exports in rares_data.items():
            # Only process if exports is a list (not an error dict)
            if isinstance(exports, list) and exports:
                for export in exports:
                    # Ensure export has systemX, systemY, systemZ
                    if (
                        hasattr(export, "systemX") and export.systemX is not None and
                        hasattr(export, "systemY") and export.systemY is not None and
                        hasattr(export, "systemZ") and export.systemZ is not None
                    ):
                        dx = export.systemX - x
                        dy = export.systemY - y
                        dz = export.systemZ - z
                        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                        rare_distances.append((commodity, export, distance))

        # Sort by distance
        rare_distances.sort(key=lambda tup: tup[2])
        return rare_distances