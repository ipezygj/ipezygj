""" Technical implementation for Hummingbot Gateway V2.1. """
import asyncio
import datetime

import httpx

from auth import NASA_API_KEY
from telegram_bot import send_alpha_alert


class StealthNEOMapper:
    """ Maps undocumented or recently discovered NEOs specifically under 100m in diameter. """
    def __init__(self, max_diameter_m: float = 100.0, max_distance_ld: float = 10.0):
        # Suodattimet: Vain alle 100m kivet, jotka tulevat lähemmäs kuin 10 Kuun etäisyyttä
        self.max_diameter = max_diameter_m
        self.max_distance_ld = max_distance_ld

    async def scan_sector(self):
        """ Hakee kuluvan päivän asteroidit ja seuloo sokean pisteen kohteet. """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key={NASA_API_KEY}"
        
        async with httpx.AsyncClient() as client:
            try:
                print("🛰️ [MAPPER] Skannataan NASA JPL -tietokantaa <100m NEO-kohteille...")
                r = await client.get(url, timeout=15.0)
                if r.status_code == 200:
                    data = r.json()
                    asteroids = data.get("near_earth_objects", {}).get(today, [])
                    
                    for ast in asteroids:
                        name = ast.get("name")
                        # Otetaan maksimiarvio halkaisijasta varmuuden vuoksi
                        diameter = ast["estimated_diameter"]["meters"]["estimated_diameter_max"]
                        # Etäisyys Lunar Distance (LD) - Kuun etäisyyksinä
                        distance_ld = float(ast["close_approach_data"][0]["miss_distance"]["lunar"])
                        speed = float(ast["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"])
                        
                        # Käsityöläisen Stealth-suodatin: Pieni ja lähellä
                        if diameter <= self.max_diameter and distance_ld <= self.max_distance_ld:
                            msg = (
                                f"🌑 *STEALTH NEO MAPPED*\n\n"
                                f"📍 *Designation:* {name}\n"
                                f"📏 *Diameter:* {diameter:.1f} meters\n"
                                f"🎯 *Miss Distance:* {distance_ld:.2f} LD (Lunar Distances)\n"
                                f"⚡ *Velocity:* {speed:.1f} km/s\n\n"
                                f"🔭 _Status: <100m Mapping Gap Target Logged_"
                            )
                            await send_alpha_alert(msg, channel="cosmic")
                            print(f"🌑 [MAPPER] Stealth-kohde kartoitettu: {name} ({diameter:.1f}m)")
                            break # Lähetetään yksi laadukas osuma per skannaus (Stealth-tyyli)
            except Exception as e:
                print(f"❌ [MAPPER] Sensorihäiriö: {e}")

async def run_deep_space_radar():
    """ Jatkuva skannausluuppi sokeille pisteille. """
    print("🛰️ [MAPPER] Stealth NEO Mapper online. Keskitytään <100m kohteisiin...")
    mapper = StealthNEOMapper() 
    
    while True:
        await mapper.scan_sector()
        await asyncio.sleep(7200) # Päivitetään kahden tunnin välein
