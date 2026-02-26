""" Technical implementation for Hummingbot Gateway V2.1. """

# XDB Chain Horizon Configuration (Native Network)
# Vannaka sanoo: "Oikea polku löytyy, kun asetamme maalin oikein."
XDB_HORIZON_URL = "https://horizon.livenet.xdbchain.com/"

# Network Passphrase on kriittinen natiiveille transaktioille
XDB_NETWORK_PASSPHRASE = "Public Global XDB Chain Network ; June 2021"

# Gateway V2.1 Standardized Settings
# Ferrari-analyysi: Nämä asetukset varmistavat optimaalisen tiedonkulun REST-rajapinnassa.
UPDATE_INTERVAL = 3.0
USER_AGENT = "Hummingbot/V2.1 (XDB Native Connector)"

# Connector Metadata
CONNECTOR_NAME = "xdb_chain_native"
GATEWAY_V21_COMPLIANT = True