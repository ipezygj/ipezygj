""" Technical implementation for Hummingbot Gateway V2.1. """
from typing import Dict, Final, List

# --- Perus säädöt ---
NETWORK_TIMEOUT_GLOBAL: Final[float] = 3.0
ADAPTIVE_JITTER_MS: Final[tuple] = (25, 480)

# --- Kaupankäynnin viisaus (The Craftsmanship Edge) ---
MIN_SPREAD_PERCENT: Final[float] = 0.15  # Minimivoitto % (kulujen jälkeen)
MAX_ORDER_SIZE_USD: Final[int] = 50      # Pidetään peli pienenä ja turvallisena
TARGET_ASSET: Final[str] = "BTC-USDT"    # Aloitetaan kuninkaasta

# --- Stealth Identity Pool ---
STEALTH_USER_AGENTS: Final[List[str]] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
]

# --- Pörssien hintarajapinnat (Ticker Endpoints) ---
# Vaihdetaan pelkät pingit oikeisiin hintoihin
ALPHA_EXCHANGE_PAYLOAD: Final[Dict[str, str]] = {
    "BINANCE": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT",
    "BITGET": "https://api.bitget.com/api/v2/spot/market/tickers?symbol=BTCUSDT",
    "BYBIT": "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT",
    "OKX": "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT",
    "KRAKEN": "https://api.kraken.com/0/public/Ticker?pair=XBTUSDT"
}
