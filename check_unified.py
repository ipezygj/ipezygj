import requests

def check_unified():
    addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
    url = "https://api.hyperliquid.xyz/info"
    
    try:
        # Kysytään koko tilin tilaa
        r = requests.post(url, json={"type": "clearinghouseState", "user": addr})
        data = r.json()
        
        # Unified Accountissa katsotaan 'withdrawable' tai 'accountValue'
        margin = data.get('marginSummary', {})
        total_value = float(margin.get('accountValue', 0))
        withdrawable = float(margin.get('withdrawableCash', 0))
        
        print(f"\n🏎️  FERRARI UNIFIED STATUS")
        print("-" * 30)
        print(f"💰 KOKONAISSALDO: ${total_value:.2f}")
        print(f"💵 KÄYTETTÄVISSÄ: ${withdrawable:.2f}")
        
        if total_value > 50:
            print("\n✅ MOOTTORI LÄMMIN. Saldo tunnistettu.")
        else:
            print("\n⏳ Saldo ei vielä näy API:ssa. Tarkista pörssisivun 'Account' -tila.")
        print("-" * 30)
    except Exception as e:
        print(f"❌ Virhe: {e}")

if __name__ == "__main__":
    check_unified()
