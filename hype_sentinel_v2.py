""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time

def get_data(addr):
    url = "https://api.hyperliquid.xyz/info"
    
    # Haetaan hinta, spot-saldo ja perp-saldo
    price = float(requests.post(url, json={"type": "allMids"}).json().get('HYPE', 0))
    spot = requests.post(url, json={"type": "spotClearinghouseState", "user": addr}).json()
    perp = requests.post(url, json={"type": "clearinghouseState", "user": addr}).json()
    
    return price, spot, perp

def run_sentinel():
    addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
    print(f"\n🏎️  SENTINEL V2 (ISOLATED MODE) - MONITORING ALL ENGINES")
    print("-" * 50)
    
    try:
        while True:
            price, spot, perp = get_data(addr)
            
            # Lasketaan Spot
            usdc_spot = 0
            hype_amount = 0
            for b in spot.get('balances', []):
                if b['coin'] == 'USDC': usdc_spot = float(b['total'])
                if b['coin'] == 'HYPE': hype_amount = float(b['total'])
            
            # Lasketaan Perp
            perp_equity = float(perp.get('marginSummary', {}).get('accountValue', 0))
            
            total_value = usdc_spot + (hype_amount * price) + perp_equity
            
            print(f"📈 HYPE: ${price:.3f} | Total: ${total_value:.2f}")
            print(f"   [Spot: ${usdc_spot + (hype_amount*price):.2f}] [Perp: ${perp_equity:.2f}]")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🏁 Sentinel pysäytetty.")
    except Exception as e:
        print(f"\n❌ Virhe: {e}")

if __name__ == "__main__":
    run_sentinel()
