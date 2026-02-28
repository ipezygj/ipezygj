""" Technical implementation for Hummingbot Gateway V2.1. """

# Vertex & Hyperliquid Public Endpoints (Strictly NO hardcoded API keys here)
VERTEX_REST_URL = "https://gateway.prod.vertexprotocol.com/v1"
VERTEX_WS_URL = "wss://gateway.prod.vertexprotocol.com/v1/ws"

HYPERLIQUID_REST_URL = "https://api.hyperliquid.xyz"
HYPERLIQUID_WS_URL = "wss://api.hyperliquid.xyz/ws"

MAX_RETRIES = 3
RATE_LIMIT_DELAY = 1.5  # Seconds
