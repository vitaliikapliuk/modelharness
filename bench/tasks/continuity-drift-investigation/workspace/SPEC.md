# Billing reports — specification

A small reporting tool that summarizes billing line items over a date window. The
modules are:

- `money.py` — monetary rounding helpers.
- `dates.py` — date parsing and window selection.
- `categorize.py` — maps each line item's `kind` to a report category.
- `report.py` — orchestrates the above into a report (do not change its shape).
- `data.py` — the fixed sample dataset used by the worked examples below.

The reports currently **drift** from the worked examples in this document. The worked
examples are the ground truth. Your job is to find and fix every defect so the code
reproduces them exactly.

## Data model

Each line item is `{"date": "YYYY-MM-DD", "kind": str, "amount": float}`.

## Money rounding

All monetary amounts are rounded to whole cents using **round-half-up**: a value
whose third decimal is exactly 5 rounds the cent UP (e.g. `0.005 -> 0.01`,
`12.345 -> 12.35`, `4.005 -> 4.01`). Rounding never truncates toward zero.

## Date windows

A window `[start, end]` is **inclusive of both endpoints**. An item dated exactly on
`start` or exactly on `end` is in the window.

## Categories

Every `kind` maps to exactly one of three categories:

| category  | meaning                                   | kinds                              |
|-----------|-------------------------------------------|------------------------------------|
| `charges` | money the customer owes us                | `subscription`, `usage`, `overage` |
| `credits` | refunds / downward adjustments we owe back | `refund`, `adjustment`, `discount` |
| `fees`    | third-party / processing fees passed through | `processing`, `gateway`          |

Note in particular that `adjustment` is a **credit**, not a fee.

## Report shape

`build_report(items, start, end)` returns:

```
{
  "window": {"start": start, "end": end},
  "totals": {"charges": float, "credits": float, "fees": float},
  "net":    float,   # round(charges - credits + fees) to cents
  "count":  int,     # number of items inside the window
}
```

Each per-category total is the round-to-cents sum of that category's item amounts
(each amount is rounded to cents first, then accumulated).

## Worked examples (ground truth)

Using the dataset in `data.py`:

### Example 1 — `build_report(ITEMS, "2024-01-01", "2024-01-31")`

```json
{
  "window": {"start": "2024-01-01", "end": "2024-01-31"},
  "totals": {"charges": 46.36, "credits": 10.14, "fees": 1.26},
  "net": 37.48,
  "count": 7
}
```

### Example 2 — `build_report(ITEMS, "2024-01-10", "2024-01-25")`

```json
{
  "window": {"start": "2024-01-10", "end": "2024-01-25"},
  "totals": {"charges": 4.01, "credits": 7.01, "fees": 1.26},
  "net": -1.74,
  "count": 4
}
```

## Success criteria

- The code reproduces both worked examples exactly.
- Every planted defect is fixed (there is more than one, in more than one module).
- The visible tests in `test_report_visible.py` still pass.
