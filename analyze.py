""" Ferrari Intelligence - Profit Potential Analytics. """
import sqlite3

def calculate_profit():
    conn = sqlite3.connect("ferrari_intelligence.db")
    cursor = conn.cursor()
    
    # Haetaan peräkkäiset hinnat ja lasketaan volatiliteetti-pohjainen tuotto
    query = """
    SELECT timestamp, price, exchange, weight 
    FROM market_data 
    WHERE weight > 0.8
    ORDER BY timestamp DESC LIMIT 100;
    """
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print("\n💰 PROFIT POTENTIAL REPORT (Theoretical)")
        print("-" * 60)
        print(f"{'Time':<10} | {'Price Gap':<12} | {'Potential %':<12} | {'Status'}")
        print("-" * 60)
        
        for i in range(len(rows) - 1):
            price_diff = abs(rows[i][1] - rows[i+1][1])
            profit_pct = (price_diff / rows[i][1]) * 100
            
            # Jos hintaero on yli 0.05% (Tyypillinen kulu-raja)
            if profit_pct > 0.05:
                status = "🚀 BOUNTY READY" if profit_pct > 0.1 else "✅ FEASIBLE"
                print(f"{int(rows[i][0]) % 100000:<10} |  | {profit_pct:<11.3f}% | {status}")
                
        print("-" * 60 + "\n")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    calculate_profit()
