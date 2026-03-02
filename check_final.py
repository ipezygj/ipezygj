import requests

def check_fuel():
    # Tämä on se Master-osoitteesi
    addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
    url = "https://api.hyperliquid.xyz/info"
    
    try:
        res = requests.post(url, json={"type": "clearinghouseState", "user": addr}).json()
        # Haetaan saldo marginSummarysta
        equity = res.get('marginSummary', {}).get('accountValue', '0.0')
        
        print(f"\n🏎️  FERRARI STATUS REPORT")
        print("-" * 30)
        print(f"📍 ADDRESS: {addr}")
        print(f"💰 TRADING BALANCE: ${float(equity):.2f} USDC")
        
        if float(equity) > 50:
            print("\n✅ TANKKI TÄYNNÄ. RADALLE!")
        else:
            print("\n⏳ ODOTETAAN TALLETUSTA...")
            print("Varmista, että painoit MetaMaskissa 'Deposit'.")
        print("-" * 30)
    except Exception as e:
        print(f"❌ VIRHE: {e}")

if __name__ == "__main__":
    check_fuel()
