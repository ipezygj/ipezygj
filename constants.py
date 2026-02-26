""" Technical implementation for Hummingbot Gateway V2.1. """

from typing import Dict, Final

# ====================================================================================================
# NETWORK ARCHITECTURE & OPTIMIZATION
# ====================================================================================================
NETWORK_TIMEOUT_GLOBAL: Final[float] = 3.0
NETWORK_TIMEOUT_CRITICAL: Final[float] = 5.0

# Connection Pooling: Keep connections warm for faster execution
MAX_CONNECTIONS: Final[int] = 100
MAX_KEEP_ALIVE_CONNECTIONS: Final[int] = 20

# Adaptive Jitter: Random delay (ms) to bypass bot detection
ADAPTIVE_JITTER_MS: Final[tuple] = (10, 500)

# ====================================================================================================
# EXCHANGE ENDPOINT REGISTRY
# ====================================================================================================
XDB_HORIZON_NODES: Final[Dict[str, str]] = {
    "MAINNET": "https://horizon.stellar.org",
    "TESTNET": "https://horizon-testnet.stellar.org",
}

ALPHA_EXCHANGE_PAYLOAD: Final[Dict[str, str]] = {
    "BINANCE": "https://api.binance.com/api/v3/ping",
    "BITGET": "https://api.bitget.com/api/v2/public/time",
    "BYBIT": "https://api.bybit.com/v5/market/time",
    "DYDX_V4": "https://indexer.dydx.trade/v4/time",
    "GATE_IO": "https://api.gateio.ws/api/v4/spot/time",
    "HYPERLIQUID": "https://api.hyperliquid.xyz/info",
    "INJECTIVE": "https://sentry.lcd.injective.network/api/v1/ping",
    "KRAKEN": "https://api.kraken.com/0/public/Time",
    "KUCOIN": "https://api.kucoin.com/api/v1/timestamp",
    "OKX": "https://www.okx.com/api/v5/public/time",
    "VERTEX": "https://prod.vertexprotocol-backend.com/v1/time",
}

STEALTH_HEADERS: Final[Dict[str, str]] = {
    "User-Agent": "Mozilla/5.0 (V2.1 Gateway Node; Institutional Grade) AppleWebKit/537.36",
    "Accept": "application/json",
}
