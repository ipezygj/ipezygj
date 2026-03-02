import requests
import json

addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555".lower()
url = "https://api.hyperliquid.xyz/info"

def check():
    payload = {"type": "clearinghouseState", "user": addr}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            equity = data.get("marginSummary", {}).get("accountValue", "0.0")
            print(f"\n🏎️  FERRARI FUEL GAUGE")
            print(f"📍 ADDR: {addr}")
            print(f"💰 USDC: ${float(equity):.2f}")
            
            if float(equity) > 0:
                print("\n✅ TANKKI TÄYNNÄ. RADALLE!")
            else:
                print("\n⏳ ODOTETAAN TANKKAUSTA (Deposit/EVM)...")
        else:
            print(f"❌ API-VIRHE: {response.status_code}")
    except Exception as e:
        print(f"❌ YHTEYSVIRHE: {e}")

if __name__ == "__main__":
    check()
