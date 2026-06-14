"""Map raw line-item kinds to the report's three buckets. See SPEC.md for the
exact kind -> category mapping."""

# Each raw item has a 'kind'. The report groups kinds into three categories:
#   charges  -> money the customer owes us
#   credits  -> money we owe the customer / refunds & downward adjustments
#   fees     -> third-party / processing fees we pass through
KIND_TO_CATEGORY = {
    "subscription": "charges",
    "usage": "charges",
    "overage": "charges",
    "refund": "credits",
    "adjustment": "credits",
    "discount": "credits",
    "processing": "fees",
    "gateway": "fees",
}


def categorize(item):
    """Return the report category for a line item based on its 'kind'.

    Unknown kinds raise KeyError (the caller validates inputs upstream).
    """
    return KIND_TO_CATEGORY[item["kind"]]
