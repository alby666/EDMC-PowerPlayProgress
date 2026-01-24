"""Trade routes data model and utilities for PowerPlay trading."""

from dataclasses import dataclass
from typing import Optional
import requests
import math
from EDMCLogging import get_plugin_logger  # type: ignore # noqa: N813
from config import appname  # type: ignore # noqa: N813
from consts import PLUGIN_NAME

logger = get_plugin_logger(f"{appname}.{PLUGIN_NAME}")


@dataclass
class TradeRoute:
    """Represents a trade route opportunity."""
    
    system_name: str
    station_name: str
    commodity_name: str
    buy_price: int
    sell_price: int
    stock: int
    demand: int
    profit_margin: float  # Percentage
    distance_ly: float
    market_id: Optional[int] = None
    max_landing_pad_size: Optional[str] = None
    updated_at: Optional[str] = None

    def get_profit_per_ton(self) -> int:
        """Calculate profit per ton."""
        return self.sell_price - self.buy_price


class TradeRoutes:
    """Manager for loading and accessing trade route data from Ardent API."""
    
    # Base URL for Ardent API
    API_BASE_URL = "https://api.ardent-insight.com/v2"
    
    # Trade route types
    ACQUISITION = "acquisition"
    REINFORCEMENT = "reinforcement"
    UNDERMINING = "undermining"
    
    # Thresholds
    MIN_PROFIT_MARGIN = 0.40  # 40% profit margin
    MAX_UNDERMINING_PRICE = 500  # Credits per ton
    
    def __init__(self):
        """Initialize the trade routes manager."""
        self.timeout = 10  # API request timeout in seconds
        
    def _make_api_request(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        """Make a request to the Ardent API.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            JSON response as dict, or None if request fails
        """
        url = f"{self.API_BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed for {url}: {e}")
            return None
    
    def _calculate_profit_margin(self, buy_price: int, sell_price: int) -> float:
        """Calculate profit margin as a percentage.
        
        Args:
            buy_price: Buy price per ton
            sell_price: Sell price per ton
            
        Returns:
            Profit margin as decimal (e.g., 0.45 for 45%)
        """
        if buy_price <= 0:
            return 0.0
        return (sell_price - buy_price) / buy_price
    
    def get_reinforcement_routes(self, system_name: str, current_x: float, current_y: float, 
                                  current_z: float, max_results: int = 5, min_stock: int = 1) -> list[TradeRoute]:
        """Get reinforcement trade routes for a system.
        
        Reinforcement trades are in systems already controlled by your power.
        Requires 40% or higher profit margin.
        
        Args:
            system_name: Name of the destination system
            current_x: Current system X coordinate
            current_y: Current system Y coordinate
            current_z: Current system Z coordinate
            max_results: Maximum number of results to return
            min_stock: Minimum stock level to filter by
            
        Returns:
            List of TradeRoute objects
        """
        # Get commodities imported by the system (where we can sell)
        imports_data = self._make_api_request(
            f"system/name/{system_name}/commodities/imports",
            params={
                "minVolume": 1,
                "minPrice": 100,
                "fleetCarriers": False,
                "maxDaysAgo": 30
            }
        )
        
        if not imports_data:
            return []
        
        routes = []
        for item in imports_data:
            # Check if this is a high-profit trade
            buy_price = item.get("buyPrice", 0)
            sell_price = item.get("sellPrice", 0)
            
            if buy_price > 0:
                profit_margin = self._calculate_profit_margin(buy_price, sell_price)
                stock = item.get("stock", 0)
                
                if profit_margin >= self.MIN_PROFIT_MARGIN and stock >= min_stock:
                    # Calculate distance
                    station_coords = item.get("coordinates", {})
                    dx = station_coords.get("x", current_x) - current_x
                    dy = station_coords.get("y", current_y) - current_y
                    dz = station_coords.get("z", current_z) - current_z
                    distance = math.sqrt(dx * dx + dy * dy + dz * dz)
                    
                    route = TradeRoute(
                        system_name=item.get("systemName", system_name),
                        station_name=item.get("stationName", "Unknown"),
                        commodity_name=item.get("commodityName", "Unknown"),
                        buy_price=buy_price,
                        sell_price=sell_price,
                        stock=stock,
                        demand=item.get("demand", 0),
                        profit_margin=profit_margin,
                        distance_ly=distance,
                        market_id=item.get("marketId"),
                        max_landing_pad_size=self._convert_pad_size(item.get("maxLandingPadSize")),
                        updated_at=item.get("updatedAt")
                    )
                    routes.append(route)
        
        # Sort by profit margin descending and limit results
        routes.sort(key=lambda r: r.profit_margin, reverse=True)
        return routes[:max_results]
    
    def get_acquisition_routes(self, source_system: str, dest_system: str, 
                               current_x: float, current_y: float, current_z: float,
                               max_results: int = 5, min_stock: int = 1) -> list[TradeRoute]:
        """Get acquisition trade routes.
        
        Acquisition trades are from fortified/stronghold systems to systems
        in control range that aren't managed yet. Requires 40% or higher profit margin.
        
        Args:
            source_system: Source system (fortified/stronghold)
            dest_system: Destination system (acquisition target)
            current_x: Current system X coordinate
            current_y: Current system Y coordinate
            current_z: Current system Z coordinate
            max_results: Maximum number of results to return
            min_stock: Minimum stock level to filter by
            
        Returns:
            List of TradeRoute objects
        """
        # Get exports from source system (where we can buy)
        exports_data = self._make_api_request(
            f"system/name/{source_system}/commodities/exports",
            params={
                "minVolume": 1,
                "fleetCarriers": False,
                "maxDaysAgo": 30
            }
        )
        
        # Get imports from destination system (where we can sell)
        imports_data = self._make_api_request(
            f"system/name/{dest_system}/commodities/imports",
            params={
                "minVolume": 1,
                "minPrice": 100,
                "fleetCarriers": False,
                "maxDaysAgo": 30
            }
        )
        
        if not exports_data or not imports_data:
            return []
        
        # Create a map of commodities we can buy
        exports_map = {
            item.get("commodityName"): item 
            for item in exports_data
        }
        
        routes = []
        for import_item in imports_data:
            commodity_name = import_item.get("commodityName")
            
            # Check if we can buy this commodity from source system
            if commodity_name in exports_map:
                export_item = exports_map[commodity_name]
                buy_price = export_item.get("sellPrice", 0)  # We buy at their sell price
                sell_price = import_item.get("buyPrice", 0)  # We sell at their buy price
                
                if buy_price > 0:
                    profit_margin = self._calculate_profit_margin(buy_price, sell_price)
                    stock = export_item.get("stock", 0)
                    
                    if profit_margin >= self.MIN_PROFIT_MARGIN and stock >= min_stock:
                        # Calculate distance
                        station_coords = import_item.get("coordinates", {})
                        dx = station_coords.get("x", current_x) - current_x
                        dy = station_coords.get("y", current_y) - current_y
                        dz = station_coords.get("z", current_z) - current_z
                        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
                        
                        route = TradeRoute(
                            system_name=import_item.get("systemName", dest_system),
                            station_name=import_item.get("stationName", "Unknown"),
                            commodity_name=commodity_name,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            stock=stock,
                            demand=import_item.get("demand", 0),
                            profit_margin=profit_margin,
                            distance_ly=distance,
                            market_id=import_item.get("marketId"),
                            max_landing_pad_size=self._convert_pad_size(import_item.get("maxLandingPadSize")),
                            updated_at=import_item.get("updatedAt")
                        )
                        routes.append(route)
        
        # Sort by profit margin descending and limit results
        routes.sort(key=lambda r: r.profit_margin, reverse=True)
        return routes[:max_results]
    
    def get_undermining_routes(self, system_name: str, current_x: float, current_y: float,
                               current_z: float, max_results: int = 5, min_stock: int = 1) -> list[TradeRoute]:
        """Get undermining trade routes.
        
        Undermining trades are cheap commodities (< 500 cr/ton) sold to
        systems controlled by rival powers.
        
        Args:
            system_name: Name of the destination system (rival power)
            current_x: Current system X coordinate
            current_y: Current system Y coordinate
            current_z: Current system Z coordinate
            max_results: Maximum number of results to return
            min_stock: Minimum stock level to filter by
            
        Returns:
            List of TradeRoute objects
        """
        # Get commodities imported by the system with low sell prices
        imports_data = self._make_api_request(
            f"system/name/{system_name}/commodities/imports",
            params={
                "minVolume": 1,
                "minPrice": 1,
                "fleetCarriers": False,
                "maxDaysAgo": 30
            }
        )
        
        if not imports_data:
            return []
        
        routes = []
        for item in imports_data:
            buy_price = item.get("buyPrice", 0)
            sell_price = item.get("sellPrice", 0)
            stock = item.get("stock", 0)
            
            # For undermining, we want cheap commodities to flood the market
            if sell_price > 0 and sell_price < self.MAX_UNDERMINING_PRICE and stock >= min_stock:
                # Calculate distance
                station_coords = item.get("coordinates", {})
                dx = station_coords.get("x", current_x) - current_x
                dy = station_coords.get("y", current_y) - current_y
                dz = station_coords.get("z", current_z) - current_z
                distance = math.sqrt(dx * dx + dy * dy + dz * dz)
                
                route = TradeRoute(
                    system_name=item.get("systemName", system_name),
                    station_name=item.get("stationName", "Unknown"),
                    commodity_name=item.get("commodityName", "Unknown"),
                    buy_price=buy_price,
                    sell_price=sell_price,
                    stock=stock,
                    demand=item.get("demand", 0),
                    profit_margin=0.0,  # Not relevant for undermining
                    distance_ly=distance,
                    market_id=item.get("marketId"),
                    max_landing_pad_size=self._convert_pad_size(item.get("maxLandingPadSize")),
                    updated_at=item.get("updatedAt")
                )
                routes.append(route)
        
        # Sort by sell price ascending (cheapest first) and limit results
        routes.sort(key=lambda r: r.sell_price)
        return routes[:max_results]
    
    def _convert_pad_size(self, pad_size: Optional[int]) -> Optional[str]:
        """Convert numeric pad size to string representation.
        
        Args:
            pad_size: Numeric pad size (1=Small, 2=Medium, 3=Large)
            
        Returns:
            String representation or None
        """
        if pad_size is None:
            return None
        
        size_map = {
            1: "Small",
            2: "Medium",
            3: "Large"
        }
        return size_map.get(pad_size, "Unknown")
