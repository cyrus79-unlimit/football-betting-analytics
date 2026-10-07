import requests
import pandas as pd
from typing import List, Dict, Any


class PolymarketScraper:
    """
    Scrapes soccer/football market odds and prediction metrics
    from Polymarket's public Gamma API.
    """

    def __init__(self):
        # Polymarket Gamma API endpoint for public market data
        self.api_url = "https://gamma-api.polymarket.com/markets"

    def fetch_football_markets(self, limit: int = 50) -> pd.DataFrame:
        """
        Queries Polymarket for active sports/soccer betting markets and
        parses probabilities and event dates.
        """
        params = {
            "limit": limit,
            "active": True,
            "closed": False,
            "tag_slug": "soccer"  # Filter specifically for soccer markets
        }

        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            parsed_markets: List[Dict[str, Any]] = []

            for market in data:
                question = market.get("question", "")

                # Standard parsing for probabilities & outcome choices
                outcomes = market.get("outcomes", [])
                outcome_prices = market.get("outcomePrices", [])

                parsed_markets.append({
                    "market_id": market.get("id"),
                    "question": question,
                    "event_slug": market.get("slug"),
                    "end_date": market.get("endDate"),
                    "volume": float(market.get("volume", 0)),
                    "outcomes": outcomes,
                    "prices": outcome_prices,
                    "scraped_at": pd.Timestamp.now()
                })

            df = pd.DataFrame(parsed_markets)
            return df

        except Exception as e:
            print(f"Error fetching data from Polymarket API: {e}")
            # Return empty DataFrame with expected columns if request fails
            return pd.DataFrame(columns=[
                "market_id", "question", "event_slug", "end_date",
                "volume", "outcomes", "prices", "scraped_at"
            ])


if __name__ == "__main__":
    scraper = PolymarketScraper()
    df = scraper.fetch_football_markets(limit=10)

    print("\n--- SAMPLE SCRAPED MARKETS ---")
    print(df[['question', 'prices', 'volume']].to_string())