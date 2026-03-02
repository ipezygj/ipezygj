import requests
addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
url = "https://api.hyperliquid.xyz/info"
payload = {"type": "clearinghouseState", "user": addr}
res = requests.post(url, json=payload).json()
print(f"\n📍 OSOITE: {addr}")
print(f"💰 L1 SALDO: ${res.get('marginSummary', {}).get('accountValue', '0.0')}")
print(f"📊 CROSS MARGIN: {res.get('crossMarginSummary', {}).get('accountValue', '0.0')}")
