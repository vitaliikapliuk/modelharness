"""Reporting over a ledger."""


def render(ledger) -> str:
    # One line per key in sorted order: "<key>: <balance>".
    lines = []
    for key in ledger.keys():
        lines.append("%s: %d" % (key, ledger.balance(key)))
    return "\n".join(lines)
