""" Technical implementation for Hummingbot Gateway V2.1. """

# API Endpoints
INFO_URL = "https://api.hyperliquid.xyz/info"
EXCHANGE_URL = "https://api.hyperliquid.xyz/exchange"

# Chain Configuration
CHAIN_ID = 1337  # Hyperliquid L1 Mainnet

# Exchange Action Types
ACTION_TYPES = {
    "ORDER": "order",
    "CANCEL": "cancel",
    "WITHDRAW": "withdraw",
}

# Default settings
DEFAULT_CURRENCY = "USDC"
