""" Technical implementation for Hummingbot Gateway V2.1. """
from typing import Dict, Final, List

# --- Core Networking ---
NETWORK_TIMEOUT_GLOBAL: Final[float] = 3.0
NETWORK_TIMEOUT_CRITICAL: Final[float] = 5.0
ADAPTIVE_JITTER_MS: Final[tuple] = (20, 450)

# --- Circuit Breaker Config ---
FAILURE_THRESHOLD: Final[int] = 3
COOLDOWN_PERIOD: Final[int] = 60

# --- Expanded Stealth Identities ---
STEALTH_USER_AGENTS: Final[List[str]] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
]
STEALTH_LANGUAGES: Final[List[str]] = ["en-US,en;q=0.9", "fi-FI,fi;q=0.8,en-US;q=0.7", "en-GB,en;q=0.9"]

# --- Endpoints ---
ALPHA_EXCHANGE_PAYLOAD: Final[Dict[str, str]] = {
    "BINANCE": "https://api.binance.com/api/v3/ping",
    "BITGET": "https://api.bitget.com/api/v2/public/time",
    "BYBIT": "https://api.bybit.com/v5/market/time",
    "GATE_IO": "https://api.gateio.ws/api/v4/spot/time",
    "HYPERLIQUID": "https://api.hyperliquid.xyz/info",
    "KRAKEN": "https://api.kraken.com/0/public/Time",
    "OKX": "https://www.okx.com/api/v5/public/time",
}
