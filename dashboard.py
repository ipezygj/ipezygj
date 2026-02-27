import csv
import os
import time

def clear_screen():
    os.system('clear')

def analyze_persistence():
    if not os.path.exists('myyntidata.csv'):
        print("Waiting for deep data... Start strategy.py first!")
        return

    while True:
        clear_screen()
        print(f"📊 --- FERRARI DEEP-PERSISTENCE MONITOR [{time.strftime('%H:%M:%S')}] ---")
        print("-" * 65)
        
        with open('myyntidata.csv', mode='r') as f:
            reader = csv.reader(f)
            data = list(reader)
        
        # Suodatetaan vain DEEP_ANALYZE -rivit
        deep_hits = [row for row in data if "DEEP_ANALYZE" in row]
        
        if not deep_hits:
            print("Scanning for Deep Alpha... No persistent gaps logged yet.")
        else:
            print(f"{'SYMBOL':<10} | {'INITIAL':<10} | {'T+1s':<10} | {'T+2s':<10} | {'STABILITY'}")
            print("-" * 65)
            
            # Näytetään viimeisimmät 8 analyysia
            for row in deep_hits[-8:]:
                symbol = row[1]
                initial = row[4]
                t1 = row[5]
                t2 = row[6]
                
                # Lasketaan pysyvyys (Stability)
                try:
                    init_val = float(initial.replace('%', ''))
                    t2_val = float(t2.replace('%', ''))
                    stability = "💪 STABLE" if t2_val > 0 else "💨 GHOST"
                except: stability = "???"
                
                print(f"{symbol:<10} | {initial:<10} | {t1:<10} | {t2:<10} | {stability}")
        
        print("-" * 65)
        print("Updating persistence metrics in 10s... (Ctrl+C to exit)")
        time.sleep(10)

if __name__ == "__main__":
    try:
        analyze_persistence()
    except KeyboardInterrupt:
        print("\nMonitorointi keskeytetty.")
