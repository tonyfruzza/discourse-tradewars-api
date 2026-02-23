# Reference data from twclone, adapted for MVP

COMMODITIES = [
    # (code, name, base_price, volatility, illegal)
    ("ORE", "Fuel Ore", 100, 20, False),
    ("ORG", "Organics", 150, 30, False),
    ("EQU", "Equipment", 200, 25, False),
]

# Port types: how each port class trades the 3 base commodities
# "buy" = port wants to buy from players (low stock)
# "sell" = port sells to players (high stock)
PORT_TYPES = [
    # (id, code, name, ore_mode, org_mode, equ_mode)
    (1, "SBB", "Port Class 1 (SBB)", "sell", "buy", "buy"),
    (2, "SSB", "Port Class 2 (SSB)", "sell", "sell", "buy"),
    (3, "BSS", "Port Class 3 (BSS)", "buy", "sell", "sell"),
    (4, "BSB", "Port Class 4 (BSB)", "buy", "sell", "buy"),
    (5, "BBS", "Port Class 5 (BBS)", "buy", "buy", "sell"),
    (6, "SBS", "Port Class 6 (SBS)", "sell", "buy", "sell"),
    (7, "BBB", "Specialty (Buy All)", "buy", "buy", "buy"),
    (8, "SSS", "Specialty (Sell All)", "sell", "sell", "sell"),
]

# MVP ship types: 3 purchasable ships
SHIP_TYPES = [
    # (id, name, holds, cost, max_fighters, max_shields, offense, defense)
    (1, "Scout Marauder", 25, 15950, 250, 100, 20, 20),
    (2, "Merchant Cruiser", 75, 41300, 2500, 400, 10, 10),
    (3, "Colonial Transport", 250, 63600, 200, 500, 6, 6),
]

# FedSpace warp topology (sectors 1-10, all bidirectional)
FEDSPACE_WARPS = [
    (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
    (2, 1), (2, 3), (2, 7), (2, 8), (2, 9), (2, 10),
    (3, 1), (3, 2), (3, 4),
    (4, 1), (4, 3), (4, 5),
    (5, 1), (5, 4), (5, 6),
    (6, 1), (6, 5),
    (7, 1), (7, 2), (7, 8),
    (8, 2), (8, 7), (8, 9),
    (9, 2), (9, 8), (9, 10),
    (10, 2), (10, 9),
]

# Port type weights for random assignment (types 1-6 favored over 7-8)
PORT_TYPE_WEIGHTS = [20, 20, 20, 15, 15, 15, 5, 5]
