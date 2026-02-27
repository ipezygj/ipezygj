""" 
V2.1 Gateway Standard - Order Execution & Slippage Control.
Calculates real execution price based on order book depth.
"""
import time

class PrecisionStriker:
    def __init__(self, fee: float = 0.001):
        self.fee = fee

    def calculate_effective_price(self, side: str, amount_usdt: float, top_price: float, top_qty: float):
        """ 
        Laskee 'todellisen' hinnan. Jos määrä (qty) ei riitä, 
        lisätään automaattinen 'Slippage Penalty'. 
        """
        available_usdt = top_price * top_qty
        
        if available_usdt >= amount_usdt:
            # Määrä riittää parhaaseen hintaan
            return top_price
        else:
            # Määrä EI riitä -> hinta huononee (simuloitu 0.1% rangaistus per puuttuva 50%)
            shortfall_ratio = (amount_usdt - available_usdt) / amount_usdt
            penalty = 1 + (shortfall_ratio * 0.002) if side == "BUY" else 1 - (shortfall_ratio * 0.002)
            return top_price * penalty

    def estimate_net_profit(self, buy_price: float, sell_price: float):
        """ Laskee puhtaan käteen jäävän voiton stablecoineissa. """
        return (sell_price / buy_price) - 1 - (self.fee * 2)

