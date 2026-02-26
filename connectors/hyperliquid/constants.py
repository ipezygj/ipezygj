""" Technical implementation for Hummingbot Gateway V2.1. """

# Hyperliquid L1 Configuration
# Vannaka says: "Precision is the difference between a hit and a miss."

BASE_URL = "https://api.hyperliquid.xyz"
INFO_URL = "https://api.hyperliquid.xyz/info"
EXCHANGE_URL = "https://api.hyperliquid.xyz/exchange"
WS_URL = "wss://api.hyperliquid.xyz/ws"

# Chain & Asset Metadata
HYPERLIQUID_CHAIN_ID = 1337
DEFAULT_ASSET_ID = 0  # Primary asset (e.g., USDC)

# Gateway V2.1 Standards
CONNECTOR_NAME = "hyperliquid"
VERSION = "1.3.1"
