""" Technical implementation for Hummingbot Gateway V2.1 / Strike One Activation. """
import requests
from auth import HyperVault

def strike_one():
    vault = HyperVault()
    address = vault.get_address()
    
    url = "https://api.hyperliquid.xyz/info"
    payload = {
        "type": "clearinghouseState",
        "user": address
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        # Haetaan tarkka Trading Equity
        margin = data.get("marginSummary", {})
        equity = margin.get("accountValue", "0.0")
        
        print(f"\n🏎️  STRIKE ONE: FERRARI ACTIVATION")
        print("-" * 40)
        print(f"📍 ADDRESS: {address}")
        print(f"💰 TRADING EQUITY: ${float(equity):.2f} USDC")
        
        if float(equity) > 0:
            print("\n✅ MOOTTORI KÄYNNISSÄ. VARAT TUNNISTETTU.")
        else:
            print("\n⚠️  HUOMIO: Saldo on vielä 0.0 API:ssa.")
            print("Varmista Hyperliquid-sivulla, että olet tehnyt 'Deposit' loppuun.")
            print("Paina 'Trade' sivulla kerran aktivoidaksesi tilin.")
        print("-" * 40)
            
    except Exception as e:
        print(f"❌ VIRHE: {e}")

if __name__ == "__main__":
    strike_one()
