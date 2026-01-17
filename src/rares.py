"""Rare commodities data model and utilities."""

from dataclasses import dataclass
from typing import Optional
import json
import math
from pathlib import Path


@dataclass
class Coordinates:
    """3D coordinate system for a star system."""

    x: float
    y: float
    z: float

    @classmethod
    def from_dict(cls, data: dict) -> "Coordinates":
        """Create Coordinates from a dictionary."""
        return cls(x=data["x"], y=data["y"], z=data["z"])

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass
class RareExport:
    """Represents a rare commodity available for export."""

    id: str
    symbol: str
    market_id: str
    category: str
    name: str
    system: str
    coordinates: Coordinates
    count: Optional[int] = None
    stationName: Optional[str] = None
    maxLandingPadSize: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "RareExport":
        """Create a RareExport from a dictionary.

        Args:
            data: Dictionary with rare commodity data

        Returns:
            RareExport instance
        """
        coords = (
            Coordinates.from_dict(data["coordinates"])
            if "coordinates" in data
            else Coordinates(0, 0, 0)
        )
        return cls(
            id=data["id"],
            symbol=data["symbol"],
            market_id=data["market_id"],
            category=data["category"],
            name=data["name"],
            system=data.get("system", ""),
            coordinates=coords,
            count=data.get("count"),
            stationName=data.get("stationName"),
            maxLandingPadSize=data.get("maxLandingPadSize"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "market_id": self.market_id,
            "category": self.category,
            "name": self.name,
            "count": self.count,
            "system": self.system,
            "coordinates": self.coordinates.to_dict(),
            "stationName": self.stationName,
            "maxLandingPadSize": self.maxLandingPadSize,
        }


class Rares:
    """Manager for loading and accessing rare commodity data."""

    def __init__(self):
        """Initialize the manager and auto-load rare commodities."""
        self.commodities: list[RareExport] = []
        self._by_id: dict[str, RareExport] = {}
        self._by_symbol: dict[str, RareExport] = {}
        self._by_system: dict[str, list[RareExport]] = {}

        # Auto-load the rare-commodities.json file
        json_file = Path(__file__).parent / "rare-commodities.json"
        if json_file.exists():
            self.load_from_file(json_file)

    def load_from_file(self, filepath: str | Path) -> None:
        """Load rare commodities from a JSON file.

        Args:
            filepath: Path to the rare-commodities.json file
        """
        with open(filepath, "r") as f:
            data = json.load(f)

        self.commodities = [RareExport.from_dict(item) for item in data]
        self._build_indexes()

    def load_from_data(self, data: list[dict]) -> None:
        """Load rare commodities from a list of dictionaries.

        Args:
            data: List of dictionaries containing rare commodity data
        """
        self.commodities = [RareExport.from_dict(item) for item in data]
        self._build_indexes()

    def _build_indexes(self) -> None:
        """Build internal indexes for quick lookups."""
        self._by_id.clear()
        self._by_symbol.clear()
        self._by_system.clear()

        for commodity in self.commodities:
            self._by_id[commodity.id] = commodity
            self._by_symbol[commodity.symbol] = commodity

            if commodity.system not in self._by_system:
                self._by_system[commodity.system] = []
            self._by_system[commodity.system].append(commodity)

    def get_by_id(self, commodity_id: str) -> Optional[RareExport]:
        """Get a rare commodity by its ID.

        Args:
            commodity_id: The commodity ID

        Returns:
            RareExport if found, None otherwise
        """
        return self._by_id.get(commodity_id)

    def get_by_symbol(self, symbol: str) -> Optional[RareExport]:
        """Get a rare commodity by its symbol.

        Args:
            symbol: The commodity symbol

        Returns:
            RareExport if found, None otherwise
        """
        return self._by_symbol.get(symbol)

    def get_by_system(self, system: str) -> list[RareExport]:
        """Get all rare commodities available in a specific system.

        Args:
            system: The system name

        Returns:
            List of RareExport commodities in that system
        """
        return self._by_system.get(system, [])

    def get_all(self) -> list[RareExport]:
        """Get all rare commodities.

        Returns:
            List of all RareExport commodities
        """
        return self.commodities.copy()

    def get_nearest_to(self, x: float, y: float, z: float) -> list[RareExport]:
        """Get all rare commodities ordered by distance from a point.

        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate

        Returns:
            List of RareExport commodities sorted by distance (nearest first)
        """
        def distance(commodity: RareExport) -> float:
            """Calculate 3D Euclidean distance."""
            dx = commodity.coordinates.x - x
            dy = commodity.coordinates.y - y
            dz = commodity.coordinates.z - z
            return math.sqrt(dx * dx + dy * dy + dz * dz)

        return sorted(self.commodities, key=distance)

    def save_to_file(self, filepath: str | Path) -> None:
        """Save rare commodities to a JSON file.

        Args:
            filepath: Path to save the rare-commodities.json file
        """
        data = [item.to_dict() for item in self.commodities]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def __len__(self) -> int:
        """Return the number of commodities loaded."""
        return len(self.commodities)

    def __getitem__(self, index: int) -> RareExport:
        """Get a commodity by index."""
        return self.commodities[index]

    def __iter__(self):
        """Iterate over all commodities."""
        return iter(self.commodities)
