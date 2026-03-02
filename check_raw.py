import requests

def check_raw():
    addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
    url = "https://api.hyperliquid.xyz/info"
    
    print(f"\n🏎️  RAAKADATA-ANALYYSI: {addr}")
    
    try:
        r = requests.post(url, json={"type": "clearinghouseState", "user": addr})
        data = r.json()
        
        margin = data.get('marginSummary', {})
        equity = margin.get('accountValue', '0.0')
        withdrawable = margin.get('withdrawableCash', '0.0')
        
        print("-" * 30)
        print(f"💰 ACCOUNT VALUE: ${float(equity):.2f}")
        print(f"💵 WITHDRAWABLE:  ${float(withdrawable):.2f}")
        
        if float(equity) > 50:
            print("\n✅ VANNKA! Varat tunnistettu API-tasolla.")
        else:
            print("\n⏳ API näyttää vielä nollaa. Varmista pörssisivun tila.")
        print("-" * 30)
        
    except Exception as e:
        print(f"❌ Virhe: {e}")

if __name__ == "__main__":
    check_raw()
