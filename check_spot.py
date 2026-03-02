import requests

def check_spot():
    addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
    url = "https://api.hyperliquid.xyz/info"
    
    print(f"\n🏎️  SPOT-SALDON TARKISTUS: {addr}")
    print("-" * 40)
    
    try:
        # Kysytään nimenomaan Spot-saldoja
        r = requests.post(url, json={"type": "spotClearinghouseState", "user": addr})
        data = r.json()
        
        balances = data.get('balances', [])
        
        if not balances:
            print("📭 Spot-salkku on tyhjä API:n mukaan.")
        else:
            for b in balances:
                coin = b.get('coin', '???')
                total = b.get('total', '0')
                print(f"💰 {coin}: {total}")
            
            print("\n✅ VANNKA! Varat löytyivät Spot-puolelta.")
            
    except Exception as e:
        print(f"❌ Virhe: {e}")
    print("-" * 40)

if __name__ == "__main__":
    check_spot()
