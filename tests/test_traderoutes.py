"""Tests for trade routes functionality."""

import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import requests

# Mock EDMC modules before importing traderoutes
sys.modules['EDMCLogging'] = MagicMock()
sys.modules['config'] = MagicMock()
sys.modules['consts'] = MagicMock()

from src.traderoutes import TradeRoutes, TradeRoute


class TestTradeRoutes(unittest.TestCase):
    """Test the TradeRoutes class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trade_routes = TradeRoutes()
    
    def test_calculate_profit_margin(self):
        """Test profit margin calculation."""
        # 40% profit margin
        margin = self.trade_routes._calculate_profit_margin(1000, 1400)
        self.assertAlmostEqual(margin, 0.4, places=2)
        
        # 50% profit margin
        margin = self.trade_routes._calculate_profit_margin(100, 150)
        self.assertAlmostEqual(margin, 0.5, places=2)
        
        # Zero buy price should return 0
        margin = self.trade_routes._calculate_profit_margin(0, 100)
        self.assertEqual(margin, 0.0)
        
        # Negative margin (loss)
        margin = self.trade_routes._calculate_profit_margin(1000, 900)
        self.assertAlmostEqual(margin, -0.1, places=2)
    
    def test_convert_pad_size(self):
        """Test pad size conversion."""
        self.assertEqual(self.trade_routes._convert_pad_size(1), "Small")
        self.assertEqual(self.trade_routes._convert_pad_size(2), "Medium")
        self.assertEqual(self.trade_routes._convert_pad_size(3), "Large")
        self.assertIsNone(self.trade_routes._convert_pad_size(None))
        self.assertEqual(self.trade_routes._convert_pad_size(999), "Unknown")
    
    @patch('src.traderoutes.requests.get')
    def test_make_api_request_success(self, mock_get):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response
        
        result = self.trade_routes._make_api_request("test/endpoint")
        
        self.assertEqual(result, {"test": "data"})
        mock_get.assert_called_once()
    
    @patch('src.traderoutes.requests.get')
    def test_make_api_request_failure(self, mock_get):
        """Test failed API request."""
        mock_get.side_effect = requests.RequestException("Connection error")
        
        result = self.trade_routes._make_api_request("test/endpoint")
        
        self.assertIsNone(result)
    
    @patch('src.traderoutes.requests.get')
    def test_get_reinforcement_routes(self, mock_get):
        """Test getting reinforcement routes."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "commodityName": "Gold",
                "systemName": "Sol",
                "stationName": "Abraham Lincoln",
                "buyPrice": 1000,
                "sellPrice": 1500,  # 50% profit margin
                "stock": 1000,
                "demand": 5000,
                "coordinates": {"x": 0, "y": 0, "z": 0},
                "maxLandingPadSize": 3,
                "marketId": 12345,
                "updatedAt": "2024-01-01T00:00:00Z"
            },
            {
                "commodityName": "Silver",
                "systemName": "Sol",
                "stationName": "Daedalus",
                "buyPrice": 500,
                "sellPrice": 600,  # 20% profit margin - should be filtered
                "stock": 2000,
                "demand": 3000,
                "coordinates": {"x": 0, "y": 0, "z": 0},
                "maxLandingPadSize": 2,
                "marketId": 12346,
                "updatedAt": "2024-01-01T00:00:00Z"
            }
        ]
        mock_get.return_value = mock_response
        
        routes = self.trade_routes.get_reinforcement_routes("Sol", 0, 0, 0, max_results=5)
        
        # Should only return routes with >= 40% profit margin
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].commodity_name, "Gold")
        self.assertAlmostEqual(routes[0].profit_margin, 0.5, places=2)
    
    @patch('src.traderoutes.requests.get')
    def test_get_undermining_routes(self, mock_get):
        """Test getting undermining routes."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "commodityName": "Hydrogen Fuel",
                "systemName": "Enemy System",
                "stationName": "Evil Station",
                "buyPrice": 100,
                "sellPrice": 200,  # Under 500 cr/t
                "stock": 10000,
                "demand": 5000,
                "coordinates": {"x": 10, "y": 10, "z": 10},
                "maxLandingPadSize": 3,
                "marketId": 99999,
                "updatedAt": "2024-01-01T00:00:00Z"
            },
            {
                "commodityName": "Platinum",
                "systemName": "Enemy System",
                "stationName": "Evil Station",
                "buyPrice": 10000,
                "sellPrice": 15000,  # Over 500 cr/t - should be filtered
                "stock": 100,
                "demand": 200,
                "coordinates": {"x": 10, "y": 10, "z": 10},
                "maxLandingPadSize": 3,
                "marketId": 99998,
                "updatedAt": "2024-01-01T00:00:00Z"
            }
        ]
        mock_get.return_value = mock_response
        
        routes = self.trade_routes.get_undermining_routes("Enemy System", 0, 0, 0, max_results=5)
        
        # Should only return routes with < 500 cr/t sell price
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].commodity_name, "Hydrogen Fuel")
        self.assertLess(routes[0].sell_price, 500)
    
    @patch('src.traderoutes.requests.get')
    def test_get_acquisition_routes(self, mock_get):
        """Test getting acquisition routes."""
        # Mock API responses for exports and imports
        def mock_api_call(url, *args, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            
            if "exports" in url:
                # Source system exports
                mock_response.json.return_value = [
                    {
                        "commodityName": "Gold",
                        "sellPrice": 1000,  # We buy at their sell price
                        "stock": 5000,
                        "coordinates": {"x": 0, "y": 0, "z": 0}
                    }
                ]
            else:
                # Destination system imports
                mock_response.json.return_value = [
                    {
                        "commodityName": "Gold",
                        "systemName": "Target System",
                        "stationName": "Target Station",
                        "buyPrice": 1500,  # We sell at their buy price (50% profit)
                        "demand": 3000,
                        "coordinates": {"x": 10, "y": 10, "z": 10},
                        "maxLandingPadSize": 3,
                        "marketId": 77777,
                        "updatedAt": "2024-01-01T00:00:00Z"
                    }
                ]
            return mock_response
        
        mock_get.side_effect = mock_api_call
        
        routes = self.trade_routes.get_acquisition_routes(
            "Source System", "Target System", 0, 0, 0, max_results=5
        )
        
        # Should return matching profitable routes
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].commodity_name, "Gold")
        self.assertGreaterEqual(routes[0].profit_margin, 0.4)


class TestTradeRoute(unittest.TestCase):
    """Test the TradeRoute dataclass."""
    
    def test_trade_route_creation(self):
        """Test creating a TradeRoute object."""
        route = TradeRoute(
            system_name="Sol",
            station_name="Abraham Lincoln",
            commodity_name="Gold",
            buy_price=1000,
            sell_price=1500,
            stock=1000,
            demand=5000,
            profit_margin=0.5,
            distance_ly=10.5,
            market_id=12345,
            max_landing_pad_size="Large",
            updated_at="2024-01-01"
        )
        
        self.assertEqual(route.system_name, "Sol")
        self.assertEqual(route.commodity_name, "Gold")
        self.assertEqual(route.profit_margin, 0.5)
    
    def test_get_profit_per_ton(self):
        """Test profit per ton calculation."""
        route = TradeRoute(
            system_name="Sol",
            station_name="Test",
            commodity_name="Gold",
            buy_price=1000,
            sell_price=1500,
            stock=0,
            demand=0,
            profit_margin=0.5,
            distance_ly=0
        )
        
        self.assertEqual(route.get_profit_per_ton(), 500)
        
        # Test with different prices
        route2 = TradeRoute(
            system_name="Sol",
            station_name="Test",
            commodity_name="Silver",
            buy_price=5000,
            sell_price=7500,
            stock=0,
            demand=0,
            profit_margin=0.5,
            distance_ly=0
        )
        
        self.assertEqual(route2.get_profit_per_ton(), 2500)


if __name__ == '__main__':
    unittest.main()
