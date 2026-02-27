""" Technical implementation for ID Scanner V1.0. """
import httpx
import asyncio

TOKEN = "8747958578:AAEKbU1p0jCPt61R8Nnd3YOIjKyw8z3ana4"

async def scan_ids():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    print("📡 Skannataan Telegramin data_payload...")
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url)
            data = r.json()
            
            found = False
            for res in data.get("result", []):
                if "message" in res:
                    chat = res["message"]["chat"]
                    title = chat.get('title', 'Private Chat')
                    chat_id = chat.get('id')
                    print(f"🎯 Löydetty kohde | Nimi: {title} | ID: {chat_id}")
                    found = True
            
            if not found:
                print("⚠️ Ei uusia viestejä. Kirjoita jotain ryhmään ja yritä uudelleen.")
        except Exception as e:
            print(f"❌ Verkkovirhe: {e}")

if __name__ == "__main__":
    asyncio.run(scan_ids())
