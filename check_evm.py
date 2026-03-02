import requests
addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
url = "https://api.hyperliquid.xyz/info"

# Tarkistetaan spot-balanssit ja EVM-tila
payload = {"type": "spotMetaAndAssetCtxs"}
try:
    # Tarkistetaan myös suoraan EVM-osoitteen saldo (JSON-RPC)
    evm_payload = {
        "method": "eth_getBalance",
        "params": [addr, "latest"],
        "id": 1,
        "jsonrpc": "2.0"
    }
    res_evm = requests.post("https://api.hyperliquid.xyz/evm", json=evm_payload).json()
    balance_hex = res_evm.get('result', '0x0')
    balance_decimal = int(balance_hex, 16) / 10**18
    
    print(f"\n📍 OSOITE: {addr}")
    print(f"💎 HYPEREVM SALDO (HYPE): {balance_decimal:.4f} HYPE")
    
    # Tarkistetaan clearinghouseState uudelleen
    payload_ch = {"type": "clearinghouseState", "user": addr}
    res_ch = requests.post(url, json=payload_ch).json()
    equity = res_ch.get('marginSummary', {}).get('accountValue', '0.0')
    print(f"💰 TRADING EQUITY: ${float(equity):.2f} USDC")
    
    if float(equity) == 0 and balance_decimal > 0:
        print("\n💡 VARAT OVAT EVM-PUOLELLA, MUTTA NE PITÄÄ VIELÄ 'DEPOSIT' KAUPANKÄYNTIIN.")
    elif float(equity) > 0:
        print("\n✅ FERRARI ON TANKATTU. VALMIINA.")
    else:
        print("\n⏳ ODOTETAAN VERKON VAHVISTUSTA...")
except Exception as e:
    print(f"Virhe: {e}")
