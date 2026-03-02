import requests
from auth import HyperVault

def execute_test():
    vault = HyperVault()
    address = vault.get_address()
    url = "https://api.hyperliquid.xyz/info"
    
    print(f"\n🏎️  KÄYNNISTETÄÄN TESTIAJO: {address}")
    
    try:
        r = requests.post(url, json={"type": "clearinghouseState", "user": address})
        data = r.json()
        
        # Unified accountissa katsotaan accountValue tai withdrawableCash
        margin = data.get('marginSummary', {})
        equity = margin.get('accountValue', '0.0')
        
        print(f"💰 API TUNNISTAA SALDON: ${float(equity):.2f}")
        
        if float(equity) > 50:
            print("\n✅ VANNKA! Moottori käy. Olemme valmiita strategiaan.")
        else:
            print("\n⏳ API näyttää vielä nollaa. Varmista, että painoit MetaMaskissa 'Enable Trading'.")
            
    except Exception as e:
        print(f"❌ Virhe yhteydessä: {e}")

if __name__ == "__main__":
    execute_test()
