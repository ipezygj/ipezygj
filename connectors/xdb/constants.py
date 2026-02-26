""" Technical implementation for Hummingbot Gateway V2.1. """

# XDB Chain Network Configuration
# Vannaka says: "Focus on the destination, and the path will reveal itself."

XDB_MAINNET_RPC = "https://rpc.xdbchain.com"
XDB_CHAIN_ID = 111  # Official Chain ID for XDB Mainnet
XDB_CURRENCY_SYMBOL = "XDB"

# Gateway V2.1 Standardized Endpoints
# Ferrari-analyysi: Nämä vakiot pitävät huolen, ettei koodissa ole "magic strings" -riskejä.
DEFAULT_GAS_LIMIT = 21000
MAX_FEE_PER_GAS = "1000000000"  # 1 Gwei oletuksena, säädetään verkon mukaan

# Connector Metadata
CONNECTOR_NAME = "xdb_chain"
GATEWAY_V21_COMPLIANT = True
