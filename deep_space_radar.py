""" Technical implementation for Hummingbot Gateway V2.1. """
import asyncio
import datetime

import httpx

from auth import NASA_API_KEY
from telegram_bot import send_alpha_alert


class StealthNEOMapper:
    """ Maps NEOs and routes data. Includes memory to prevent spam. """
    def __init__(self, stealth_diameter_m: float = 100.0, stealth_distance_ld: float = 10.0):
        self.stealth_diameter = stealth_diameter_m
        self.stealth_distance_ld = stealth_distance_ld
        self.alerted_targets = set() # 🧠 KÄSITYÖLÄISEN MUISTIPIIRI

    async def scan_sector(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key={NASA_API_KEY}"
        
        async with httpx.AsyncClient() as client:
            try:
                print("🛰️ [RADAR] Skannataan NASA JPL -tietokantaa...")
                r = await client.get(url, timeout=15.0)
                if r.status_code == 200:
                    data = r.json()
                    asteroids = data.get("near_earth_objects", {}).get(today, [])
                    
                    stealth_found = False
                    public_found = False
                    
                    for ast in asteroids:
                        name = ast.get("name")
                        
                        # Jos tämä kivi on jo ammuttu tänään, ohitetaan se heti!
                        if name in self.alerted_targets:
                            continue
                            
                        diameter = ast["estimated_diameter"]["meters"]["estimated_diameter_max"]
                        distance_ld = float(ast["close_approach_data"][0]["miss_distance"]["lunar"])
                        speed = float(ast["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"])
                        
                        # 💎 VIP EXCLUSIVE
                        if diameter <= self.stealth_diameter and distance_ld <= self.stealth_distance_ld and not stealth_found:
                            msg = (
                                f"💎 *VIP EXCLUSIVE: STEALTH NEO MAPPED*\n\n"
                                f"📍 *Designation:* {name}\n"
                                f"📏 *Diameter:* {diameter:.1f} meters\n"
                                f"🎯 *Miss Distance:* {distance_ld:.2f} LD\n"
                                f"⚡ *Velocity:* {speed:.1f} km/s\n\n"
                                f"🔭 _Status: <100m Mapping Gap Target Logged_"
                            )
                            await send_alpha_alert(msg, channel="vip")
                            print(f"💎 [VIP] Uusi Stealth-kohde lukittu: {name}")
                            self.alerted_targets.add(name) # Merkataan muistiin!
                            stealth_found = True
                            
                        # ☄️ PUBLIC & VIP
                        elif diameter > 500.0 and not public_found:
                            msg_public = (
                                f"☄️ *PUBLIC RADAR: MASSIVE NEO DETECTED*\n\n"
                                f"📍 *Target:* {name}\n"
                                f"📏 *Estimated Size:* {diameter:.0f} meters\n"
                                f"🔭 _Status: Standard JPL Tracking Active_\n\n"
                                f"🔒 *Want real-time alerts for undocumented sub-100m targets? Join the VIP Elite.*"
                            )
                            await send_alpha_alert(msg_public, channel="cosmic")
                            
                            msg_vip = (
                                f"☄️ *MASSIVE NEO DETECTED*\n\n"
                                f"📍 *Target:* {name}\n"
                                f"📏 *Estimated Size:* {diameter:.0f} meters\n"
                                f"🔭 _Status: Standard JPL Tracking Active_"
                            )
                            await send_alpha_alert(msg_vip, channel="vip")
                            
                            print(f"☄️ [ALL] Uusi iso kohde reititetty: {name}")
                            self.alerted_targets.add(name) # Merkataan muistiin!
                            public_found = True
                            
            except Exception as e:
                print(f"❌ [RADAR] Sensorihäiriö: {e}")

async def run_deep_space_radar():
    """ Jatkuva skannausluuppi. """
    print("🛰️ [RADAR] Dual-Pipe Radar online. Memory module active (No Spam).")
    mapper = StealthNEOMapper() 
    
    while True:
        await mapper.scan_sector()
        await asyncio.sleep(7200)
