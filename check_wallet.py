import requests

def check_all():
    addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
    url = "https://api.hyperliquid.xyz/info"
    
    # 1. Tarkista pörssisaldoa (Trading)
    res_trade = requests.post(url, json={"type": "clearinghouseState", "user": addr}).json()
    equity = res_trade.get('marginSummary', {}).get('accountValue', '0.0')
    
    # 2. Tarkista lompakon saldo (HyperEVM)
    res_wallet = requests.post(url, json={"type": "web3AssetContexts", "user": addr}).json()
    
    print(f"\n📍 OSOITE: {addr}")
    print(f"💰 TRADING SALDO: ${float(equity):.2f}")
    
    # Etsitään USDC lompakosta
    wallet_usdc = 0.0
    for asset in res_wallet:
        if asset.get('token', {}).get('name') == 'USDC':
            wallet_usdc = float(asset.get('balance', 0))
    
    print(f"👛 LOMPAKON SALDO: ${wallet_usdc:.2f}")
    
    if wallet_usdc > 50 and float(equity) == 0:
        print("\n👉 VARAT OVAT LOMPAKOSSA! Paina pörssissä 'Deposit from HyperEVM'.")
    elif float(equity) > 50:
        print("\n✅ KAIKKI VALMIINA! Varat ovat kaupankäyntitilillä.")

check_all()
