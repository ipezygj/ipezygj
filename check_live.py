""" Technical implementation for Hummingbot Gateway V2.1 / Live Status Check. """
import requests
from auth import HyperVault

def check_live_status():
    vault = HyperVault()
    address = vault.get_address()
    
    print(f"\n🏎️  FERRARI STATUS CHECK")
    print("-" * 40)
    print(f"📍 ADDRESS: {address}")
    
    url = "https://api.hyperliquid.xyz/info"
    headers = {"Content-Type": "application/json"}
    payload = {
        "type": "clearinghouseState",
        "user": address
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Haetaan saldo (withdrawable margin tai margin summary)
            margin_summary = data.get("marginSummary", {})
            account_value = margin_summary.get("accountValue", "0.0")
            
            print(f"💰 ACCOUNT VALUE: ${float(account_value):.2f} USDC")
            print(f"🕵️  STATUS: {'CONNECTION SECURE' if float(account_value) >= 0 else 'EMPTY TANK'}")
            print("-" * 40)
            
            if float(account_value) > 0:
                print("✅ MISSION READY: CAPITAL DETECTED.")
            else:
                print("⚠️  MISSION STANDBY: WAITING FOR DEPOSIT.")
        else:
            print(f"❌ API ERROR: {response.status_code}")
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")

if __name__ == "__main__":
    check_live_status()
