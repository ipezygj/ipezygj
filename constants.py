""" Technical implementation for Hummingbot Gateway V2.1. """
from typing import Dict, Final, List

# --- Technical Parameters for Connectivity Proof ---
NETWORK_TIMEOUT_GLOBAL: Final[float] = 3.0
ADAPTIVE_JITTER_MS: Final[tuple] = (50, 500)

# --- Public Endpoints (For connectivity testing) ---
ALPHA_EXCHANGE_PAYLOAD: Final[Dict[str, str]] = {
    "BINANCE": "https://api.binance.com/api/v3/ping",
    "BYBIT": "https://api.bybit.com/v5/market/time",
    "OKX": "https://www.okx.com/api/v5/public/time",
    "KRAKEN": "https://api.kraken.com/0/public/Time"
}

# --- Standard Headers ---
STEALTH_USER_AGENTS: Final[List[str]] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"
]
