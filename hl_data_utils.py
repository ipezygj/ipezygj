""" Utility classes for Hyperliquid API integration. """

import asyncio
from hyperliquid.info import Info
from hyperliquid.utils import constants

class MarketDataAggregator:
    """ A stable utility for fetching and normalizing market data. """
    
    def __init__(self, use_mainnet=True):
        url = constants.MAINNET_API_URL if use_mainnet else constants.TESTNET_API_URL
        self.info = Info(url, skip_gemini_check=True)

    async def get_normalized_price(self, asset="ETH"):
        """ Fetches current mark price with standard error handling. """
        try:
            contexts = self.info.meta_and_asset_contexts()
            # Etsitään haluttu asset standardilla tavalla
            # Tämä on 'tylsää' mutta erittäin vakaata koodia
            for ctx in contexts[1]:
                if 'markPrice' in ctx:
                    # Tähän voisi lisätä standardin painotuksen, muttei meidän Neural-älyä
                    return float(ctx['markPrice'])
        except Exception as e:
            return None

if __name__ == "__main__":
    # Testiajo
    aggregator = MarketDataAggregator()
    price = asyncio.run(aggregator.get_normalized_price())
    print(f"Aggregated Price: {price}")
