import requests
import pandas as pd
from typing import List, Dict, Any


class PolymarketScraper:
    """
    Scrapes soccer/football market odds and prediction metrics
    from Polymarket's public Gamma API.
    """

    def __init__(self):
        # Polymarket Gamma API endpoint for event-level sports markets
        self.api_url = "https://gamma-api.polymarket.com/events"

    def fetch_football_markets(self, limit: int = 50) -> pd.DataFrame:
        params = {
            "limit": limit,
            "active": True,
            "closed": False,
            "tag_slug": "soccer",  # Standard slug filter for soccer/football
            "order": "volume24hr",
            "ascending": False,
        }

        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            events = response.json()

            parsed_markets: List[Dict[str, Any]] = []

            for event in events:
                title = event.get("title", "")
                event_slug = event.get("slug", "")

                # Retrieve child markets under each match event
                markets = event.get("markets", [])
                for market in markets:
                    question = market.get("question", title)

                    # Safe parsing for ISO date format across endpoint variations
                    end_date = market.get("endDate") or market.get("end_date") or event.get("endDate")

                    parsed_markets.append({
                        "market_id": market.get("id"),
                        "question": question,
                        "event_slug": event_slug,
                        "end_date": end_date,
                        "volume": float(market.get("volume", 0)),
                        "outcomes": market.get("outcomes", []),
                        "prices": market.get("outcomePrices", []),
                        "scraped_at": pd.Timestamp.now(),
                    })

            return pd.DataFrame(parsed_markets)

        except Exception as e:
            print(f"Error fetching data from Polymarket API: {e}")
            return pd.DataFrame()


if __name__ == "__main__":
    scraper = PolymarketScraper()
    df = scraper.fetch_football_markets(limit=10)

    print("\n--- SAMPLE SCRAPED MARKETS ---")
    if not df.empty:
        print(df[["question", "prices", "volume"]].to_string())
    else:
        print("No active soccer markets found or API request failed.")