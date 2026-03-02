""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time

def get_hype_price():
    url = "https://api.hyperliquid.xyz/info"
    r = requests.post(url, json={"type": "allMids"})
    data = r.json()
    return float(data.get('HYPE', 0))

def run_sentinel():
    addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
    url = "https://api.hyperliquid.xyz/info"
    
    print(f"\n🏎️  SENTINEL ACTIVE - MONITORING HYPE")
    print("-" * 40)
    
    try:
        while True:
            price = get_hype_price()
            r = requests.post(url, json={"type": "spotClearinghouseState", "user": addr})
            balances = r.json().get('balances', [])
            
            usdc = 0
            hype_amount = 0
            for b in balances:
                if b['coin'] == 'USDC': usdc = float(b['total'])
                if b['coin'] == 'HYPE': hype_amount = float(b['total'])
            
            total_value = usdc + (hype_amount * price)
            
            print(f"📈 HYPE: ${price:.3f} | Salkku: ${total_value:.2f} (USDC: {usdc:.1f} | HYPE: {hype_amount:.2f})")
            time.sleep(10) # Päivitys 10 sekunnin välein
            
    except KeyboardInterrupt:
        print("\n🏁 Sentinel pysäytetty.")
    except Exception as e:
        print(f"\n❌ Virhe: {e}")

if __name__ == "__main__":
    run_sentinel()
