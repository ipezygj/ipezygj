import requests

def check():
    addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
    networks = {
        "MAINNET": "https://api.hyperliquid.xyz/info",
        "TESTNET": "https://api.hyperliquid.testnet.xyz/info"
    }
    
    print(f"\n🏎️  DUAL NETWORK CHECK: {addr}")
    print("-" * 40)
    
    for name, url in networks.items():
        try:
            r = requests.post(url, json={"type": "clearinghouseState", "user": addr}, timeout=5)
            data = r.json()
            equity = data.get('marginSummary', {}).get('accountValue', '0.0')
            print(f"📡 {name:8}: ${float(equity):.2f}")
        except:
            print(f"📡 {name:8}: Connection Error")
            
    print("-" * 40)

check()
