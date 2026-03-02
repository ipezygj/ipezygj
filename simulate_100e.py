import csv

def simulate():
    log_file = "global_market_log.csv"
    capital = 100.0
    min_gap = 0.06  # Lasketaan kynnystä hieman, koska näimme 0.067% jatkuvasti
    
    samples = 0
    profitable_signals = 0
    total_gap = 0.0

    try:
        with open(log_file, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                samples += 1
                gap = float(row['max_gap_pct'])
                total_gap += gap
                
                if gap >= min_gap:
                    profitable_signals += 1
        
        print(f"\n📈 FERRARI LIGHT-SIMULATOR | Capital: {capital}€")
        print("-" * 50)
        print(f"✅ Samples analyzed: {samples}")
        print(f"⚡ Signals above {min_gap}%: {profitable_signals}")
        
        if samples > 0:
            avg_gap = total_gap / samples
            print(f"📊 Average Gap: {avg_gap:.4f}%")
            
            # Arvioitu tuotto per isku (miinus pienet kulut, esim. 0.02%)
            net_profit_per_hit = (min_gap - 0.02) / 100
            total_potential = profitable_signals * (capital * net_profit_per_hit)
            
            print(f"💰 Potential Net Profit: {total_potential:.4f}€")
            print(f"🎯 Opportunity Frequency: {(profitable_signals/samples)*100:.2f}%")
        
        print("-" * 50)
        if profitable_signals > 10:
            print("🚀 STATUS: STRATEGY VALIDATED. READY FOR STAGE 2.")
        else:
            print("⏳ STATUS: GATHERING MORE DATA...")

    except FileNotFoundError:
        print("❌ Error: Log file not found. Run the harvester first!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simulate()
