""" Technical implementation for Lightweight Alpha Telemetry V1.0. """

def generate_text_chart(history):
    """ Piirtää tekstipohjaisen käyrän voiton kehityksestä. """
    if not history: return "Ei dataa."
    
    profits = [p[1] for p in history]
    cumulative = []
    curr = 0
    for p in profits:
        curr += p
        cumulative.append(curr)
    
    # Tehdään simppeli visuaalinen esitys
    max_val = max(cumulative) if cumulative else 1
    chart = "📊 *ALPHA PERFORMANCE CHART*\n```\n"
    
    for val in cumulative:
        bar_len = int((val / max_val) * 15) if max_val > 0 else 0
        chart += f"{val:6.2f}€ |" + "█" * bar_len + "\n"
    
    chart += "```"
    return chart
