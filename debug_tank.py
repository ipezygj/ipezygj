import getpass, json
from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.utils import constants

print("🔍 FERRARI DIAGNOSTICS")
key = getpass.getpass("🔑 Private Key: ")
if not key.startswith("0x"): key = "0x" + key
addr = Account.from_key(key).address
info = Info(constants.MAINNET_API_URL, skip_ws=True)

try:
    print(f"Checking wallet: {addr}...")
    state = info.user_state(addr)
    
    print("\n--- MARGIN SUMMARY (BENSA) ---")
    # Tulostetaan vain marginSummary nähdäksemme oikeat avaimet
    if "marginSummary" in state:
        print(json.dumps(state["marginSummary"], indent=2))
    elif "crossMarginSummary" in state:
        print("Huomio: Cross Margin käytössä")
        print(json.dumps(state["crossMarginSummary"], indent=2))
    else:
        print("VAROITUS: Ei margin-dataa! Koko state:")
        print(state.keys())

except Exception as e:
    print(f"❌ VIRHE: {e}")
