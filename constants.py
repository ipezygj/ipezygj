""" Technical implementation for Hummingbot Gateway V2.1. """
from typing import Dict, Final, List

# --- Perus säädöt ---
NETWORK_TIMEOUT_GLOBAL: Final[float] = 3.0
NETWORK_TIMEOUT_CRITICAL: Final[float] = 5.0
ADAPTIVE_JITTER_MS: Final[tuple] = (25, 480)

# --- Käsin poimitut nimet (Stealth Identity Pool) ---
STEALTH_USER_AGENTS: Final[List[str]] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0.0.0"
]

# --- Kaikki Hummingbot-liittimet ---
ALPHA_EXCHANGE_PAYLOAD: Final[Dict[str, str]] = {
    "BINANCE": "https://api.binance.com/api/v3/ping",
    "BITGET": "https://api.bitget.com/api/v2/public/time",
    "BYBIT": "https://api.bybit.com/v5/market/time",
    "GATE_IO": "https://api.gateio.ws/api/v4/spot/time",
    "HYPERLIQUID": "https://api.hyperliquid.xyz/info",
    "KRAKEN": "https://api.kraken.com/0/public/Time",
    "OKX": "https://www.okx.com/api/v5/public/time",
    "KUCOIN": "https://api.kucoin.com/api/v1/timestamp",
    "ASCENDEX": "https://ascendex.com/api/pro/v1/time",
    "MEXC": "https://api.mexc.com/api/v3/time",
    "HUOBI": "https://api.huobi.pro/v1/common/timestamp",
    "COINBASE": "https://api.exchange.coinbase.com/products",
    "DYDX_V4": "https://indexer.dydx.trade/v4/time",
    "VERTEX": "https://prod.vertexprotocol-backend.com/v1/time"
}
