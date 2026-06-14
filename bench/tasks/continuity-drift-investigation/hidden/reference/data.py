"""Fixed sample dataset used by SPEC.md's worked examples and the visible tests."""

ITEMS = [
    # date          kind            amount
    {"date": "2024-01-01", "kind": "subscription", "amount": 30.00},
    {"date": "2024-01-05", "kind": "usage",        "amount": 12.345},
    {"date": "2024-01-10", "kind": "overage",      "amount": 4.005},
    {"date": "2024-01-15", "kind": "processing",   "amount": 1.255},
    {"date": "2024-01-20", "kind": "refund",       "amount": 5.00},
    {"date": "2024-01-25", "kind": "adjustment",   "amount": 2.005},
    {"date": "2024-01-31", "kind": "discount",     "amount": 3.125},
    {"date": "2024-02-01", "kind": "gateway",      "amount": 0.99},
    {"date": "2024-02-05", "kind": "subscription", "amount": 30.00},
]
