import requests

def fast_check():
    addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
    url = "https://api.hyperliquid.xyz/info"
    
    # Tarkistetaan vain Trading saldo
    try:
        r = requests.post(url, json={"type": "clearinghouseState", "user": addr})
        if r.status_code == 200:
            data = r.json()
            equity = data.get('marginSummary', {}).get('accountValue', '0.0')
            print(f"\n🏎️  TRADING ACCOUNT: ${float(equity):.2f} USDC")
            if float(equity) > 50:
                print("✅ VALMIINA KAUPOILLE!")
            else:
                print("⏳ Tyhjää näyttää. Tarkista MetaMaskin 'Deposit from HyperEVM' -nappi.")
        else:
            print(f"❌ API Virhe: {r.status_code}")
    except Exception as e:
        print(f"❌ Yhteysvirhe: {e}")

if __name__ == "__main__":
    fast_check()
