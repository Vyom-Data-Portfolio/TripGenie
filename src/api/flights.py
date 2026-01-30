"""
Flight Search Integration with Amadeus API
Handles real flight search and pricing
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import json

from ..core.config import config

class FlightOffer(BaseModel):
    """Single flight offer"""
    price_usd: float
    airline: str
    departure_time: str
    arrival_time: str
    duration_hours: float
    stops: int
    cabin_class: str
    booking_url: Optional[str] = None

class FlightSearchResult(BaseModel):
    """Flight search results"""
    origin: str
    destination: str
    date: str
    offers: List[FlightOffer]
    search_success: bool = True
    error_message: Optional[str] = None

class AmadeusFlightAPI:
    """
    Amadeus Flight API Integration
    Handles authentication and search
    """
    
    def __init__(self):
        self.api_key = config.AMADEUS_API_KEY
        self.api_secret = config.AMADEUS_API_SECRET
        self.base_url = "https://test.api.amadeus.com/v2"  # Test environment
        self.access_token = None
        self.token_expires_at = None
        
    def _get_access_token(self) -> str:
        """Get OAuth2 access token"""
        
        # Check if token is still valid
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token
        
        # Get new token
        auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        
        try:
            response = requests.post(
                auth_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.api_key,
                    'client_secret': self.api_secret
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                # Token expires in X seconds
                expires_in = data.get('expires_in', 1800)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                return self.access_token
            else:
                raise Exception(f"Auth failed: {response.text}")
                
        except Exception as e:
            print(f"Amadeus auth error: {e}")
            return None
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        cabin_class: str = "ECONOMY"
    ) -> FlightSearchResult:
        """
        Search for flights
        
        Args:
            origin: IATA airport code (e.g., 'JFK')
            destination: IATA airport code (e.g., 'BKK')
            departure_date: Date in YYYY-MM-DD format
            return_date: Optional return date
            adults: Number of adult travelers
            cabin_class: ECONOMY, BUSINESS, FIRST
            
        Returns:
            FlightSearchResult with offers
        """
        
        token = self._get_access_token()
        if not token:
            return FlightSearchResult(
                origin=origin,
                destination=destination,
                date=departure_date,
                offers=[],
                search_success=False,
                error_message="Authentication failed"
            )
        
        # Build search parameters
        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date,
            'adults': adults,
            'travelClass': cabin_class,
            'max': 5  # Limit results
        }
        
        if return_date:
            params['returnDate'] = return_date
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/shopping/flight-offers",
                headers=headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                offers = self._parse_flight_offers(data)
                
                return FlightSearchResult(
                    origin=origin,
                    destination=destination,
                    date=departure_date,
                    offers=offers,
                    search_success=True
                )
            else:
                return FlightSearchResult(
                    origin=origin,
                    destination=destination,
                    date=departure_date,
                    offers=[],
                    search_success=False,
                    error_message=f"API error: {response.status_code}"
                )
                
        except Exception as e:
            return FlightSearchResult(
                origin=origin,
                destination=destination,
                date=departure_date,
                offers=[],
                search_success=False,
                error_message=str(e)
            )
    
    def _parse_flight_offers(self, data: Dict) -> List[FlightOffer]:
        """Parse Amadeus API response into FlightOffers"""
        offers = []
        
        for item in data.get('data', [])[:5]:  # Top 5 offers
            try:
                price = float(item['price']['total'])
                
                # Get first itinerary segment
                segments = item['itineraries'][0]['segments']
                first_seg = segments[0]
                last_seg = segments[-1]
                
                airline = first_seg['carrierCode']
                departure = first_seg['departure']['at']
                arrival = last_seg['arrival']['at']
                
                # Calculate duration
                duration_str = item['itineraries'][0]['duration']
                # Parse PT2H30M format
                hours = 0
                if 'H' in duration_str:
                    hours = int(duration_str.split('PT')[1].split('H')[0])
                
                offer = FlightOffer(
                    price_usd=price,
                    airline=airline,
                    departure_time=departure,
                    arrival_time=arrival,
                    duration_hours=hours,
                    stops=len(segments) - 1,
                    cabin_class=item['travelerPricings'][0]['fareDetailsBySegment'][0]['cabin']
                )
                
                offers.append(offer)
                
            except Exception as e:
                print(f"Error parsing offer: {e}")
                continue
        
        return offers
    
    def get_mock_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        **kwargs
    ) -> FlightSearchResult:
        """
        Mock flight data for testing without API calls
        """
        offers = [
            FlightOffer(
                price_usd=450.00,
                airline="TG",
                departure_time=f"{departure_date}T10:30:00",
                arrival_time=f"{departure_date}T18:45:00",
                duration_hours=8.25,
                stops=0,
                cabin_class="ECONOMY"
            ),
            FlightOffer(
                price_usd=385.00,
                airline="SQ",
                departure_time=f"{departure_date}T14:15:00",
                arrival_time=f"{departure_date}T23:30:00",
                duration_hours=9.25,
                stops=1,
                cabin_class="ECONOMY"
            ),
            FlightOffer(
                price_usd=520.00,
                airline="EK",
                departure_time=f"{departure_date}T08:00:00",
                arrival_time=f"{departure_date}T16:20:00",
                duration_hours=8.33,
                stops=0,
                cabin_class="ECONOMY"
            )
        ]
        
        return FlightSearchResult(
            origin=origin,
            destination=destination,
            date=departure_date,
            offers=offers,
            search_success=True
        )

# Global instance
flight_api = AmadeusFlightAPI()
