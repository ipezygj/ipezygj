""" Technical implementation for Hummingbot Gateway V2.1 - ANALYST V1.0 """
import csv, time, os
from hyperliquid.info import Info
from hyperliquid.utils import constants

print("📊 FERRARI ANALYST - NEUVOSTON SUORITUSKYKY")
print("------------------------------------------")

info = Info(constants.MAINNET_API_URL, skip_ws=True)
SHADOW_LOG = "shadow_data.csv"

if not os.path.exists(SHADOW_LOG):
    print("❌ Ei Shadow-dataa vielä. Anna botin kerätä dataa hetki.")
    exit()

mids = info.all_mids()
results = {"VETO_CORRECT": 0, "VETO_WRONG": 0, "LIVE_WIN": 0, "LIVE_LOSS": 0}

with open(SHADOW_LOG, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        coin = row['coin']
        orig_price = float(row['price'])
        current_price = float(mids.get(coin, orig_price))
        status = row['status']
        signal = row['signal']
        
        # Analysoidaan olisiko kauppa kannattanut
        diff_pct = (current_price - orig_price) / orig_price
        if signal == "SHORT": diff_pct = -diff_pct
        
        if "VETO" in status:
            if diff_pct > 0.005: # Olisi noussut yli 0.5%
                results["VETO_WRONG"] += 1
            else:
                results["VETO_CORRECT"] += 1
        elif "LIVE" in status:
            if diff_pct > 0.01:
                results["LIVE_WIN"] += 1
            elif diff_pct < -0.01:
                results["LIVE_LOSS"] += 1

print(f"✅ Veto-oikeus oli OIKEASSA: {results['VETO_CORRECT']} kertaa (Säästi rahaa/aikaa)")
print(f"❌ Veto-oikeus oli VÄÄRÄSSÄ: {results['VETO_WRONG']} kertaa (Menetetty mahdollisuus)")
print(f"💰 Toteutuneet Live-kaupat: {results['LIVE_WIN']} Voitollista / {results['LIVE_LOSS']} Tappiollista")
print("-" * 42)

# Ehdotus painoarvoiksi
if results['VETO_WRONG'] > results['VETO_CORRECT']:
    print("💡 SUOSITUS: Neuvosto on liian tiukka. Löysää Sentinelin tai Oraakkelin ehtoja.")
else:
    print("💡 SUOSITUS: Neuvosto toimii optimaalisesti. Pidetään linja.")
