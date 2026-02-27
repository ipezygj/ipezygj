""" Technical implementation for Order Book Imbalance Engine V1.0. """

def calculate_imbalance(bids, asks, depth=10):
    """ Laskee tilauskirjan epätasapainon valitulta syvyydeltä. """
    # Lasketaan tarjousten kokonaisvolyymi
    bid_vol = sum([float(bid[1]) for bid in bids[:depth]])
    ask_vol = sum([float(ask[1]) for ask in asks[:depth]])
    
    total_vol = bid_vol + ask_vol
    if total_vol == 0: return 0
    
    # Imbalance: 1.0 = täysi ostopaine, -1.0 = täysi myyntipaine
    imbalance = (bid_vol - ask_vol) / total_vol
    return imbalance
