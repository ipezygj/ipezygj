import requests
import time
import json
from auth import HyperVault
from eth_account import Account
import eth_abi

def force_deposit():
    vault = HyperVault()
    pk = vault.master_key
    addr = vault.get_address()

    # Hyperliquid L1 Deposit Action
    # Siirretään 90 USDC HyperEVM -> Trading
    timestamp = int(time.time() * 1000)
    action = {
        "type": "usdPoolDeposit",
        "user": addr,
        "amount": "90.0"
    }

    print(f"🚀 KÄYNNISTETÄÄN SIIRTO: 90 USDC -> TRADING")
    # Tässä vaiheessa tarvitsemme allekirjoituksen, mutta kokeillaan ensin
    # näkeekö API saldon suoraan.
    url = "https://api.hyperliquid.xyz/info"
    res = requests.post(url, json={"type": "clearinghouseState", "user": addr}).json()
    print(f"💰 NYKYINEN TRADING SALDO: ${res.get('marginSummary', {}).get('accountValue', '0.0')}")

if __name__ == "__main__":
    force_deposit()
