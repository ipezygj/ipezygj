import requests

class HyperGhost:
    def __init__(self):
        self.url = "https://api.hyperliquid.xyz/info"
        self.headers = {"Content-Type": "application/json"}

    def get_price(self, coin="ETH"):
        payload = {"type": "allMids"}
        try:
            response = requests.post(self.url, json=payload, headers=self.headers, timeout=10)
            data = response.json()
            
            # allMids palauttaa sanakirjan: {"BTC": "64000.1", "ETH": "3450.5", ...}
            price = data.get(coin)
            if price:
                return float(price)
            
            # Jos ETH ei löydy, kokeillaan etsiä muita samankaltaisia
            print(f"🕵️ Debug: {coin} not in allMids. Keys: {list(data.keys())[:5]}")
            return None
        except Exception as e:
            print(f"🕵️ Ghost Link Error: {e}")
            return None

if __name__ == "__main__":
    ghost = HyperGhost()
    price = ghost.get_price("ETH")
    print("\n🏎️ FERRARI GHOST LINK | Hyperliquid L1")
    print("-" * 40)
    if price:
        print(f"❄️ ETH Price: {price:.2f} USD")
        print("🕵️ Status: INVISIBLE & FAST")
    else:
        print("❄️ ETH Price: STILL NOT FOUND")
