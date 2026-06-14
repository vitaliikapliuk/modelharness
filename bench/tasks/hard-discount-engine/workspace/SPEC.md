# discount engine spec

```python
compute_price(base_cents: int, customer: dict, cart: dict, coupons: list[dict]) -> dict
```

Returns:

```python
{
  "final_cents": int,
  "applied": list[str],         # identifiers of discounts applied, in application order
  "rejected": list[tuple[str, str]],  # (code, reason) in the order rejection is decided
}
```

This spec is exhaustive. Every numbered rule is normative and is tested. Where rules
interact, the precise interaction is specified — implement exactly what is written.

## Data shapes

A coupon dict has these fields:

```python
{
  "code": str,            # unique-ish identifier; duplicates handled by rule 10
  "kind": "pct" | "fixed",
  "value": int,           # for "pct": basis points (1550 == 15.5%); for "fixed": cents
  "min_cart_cents": int,  # optional; default 0 if absent
  "stackable": bool,      # optional; default True if absent
}
```

`customer` has at least `{"tier": str}` where tier is `"gold"`, `"silver"`, or anything
else (treated as no tier). `cart` has at least `{"items": int}`.

## Rules

1. **Integer cents only.** All money is integer cents. A percentage discount of `v`
   basis points on an amount `A` removes `round_half_up(A * v / 10000)` cents, where
   `round_half_up(x)` rounds to the nearest integer with ties going away from zero
   (i.e. `0.5 -> 1`, `2.5 -> 3`). Rounding happens at **each** application step, on the
   running price at that step — never deferred or batched.

2. **Coupon ordering.** Coupons are evaluated in input order, **except** that all
   `pct` coupons are evaluated before all `fixed` coupons, regardless of input order.
   Within each kind, the original input order is preserved (stable). Rejections for
   reasons that can be decided without ordering (rules 10 and 11) are still surfaced in
   this same reordered evaluation order. The `tier` discount (rule 7) is applied before
   any coupon.

3. **Coupon fields.** Defaults: a coupon with no `min_cart_cents` is treated as
   `min_cart_cents == 0`; a coupon with no `stackable` is treated as `stackable ==
   True`.

4. **Non-stackable coupons.**
   - When a `stackable == False` coupon is reached and **at least one coupon has
     already been applied**, it is rejected with reason `"not_stackable"`.
   - When a `stackable == False` coupon is reached and **no coupon has been applied
     yet**, it applies (subject to the other rules), and then **every later coupon** is
     rejected with reason `"blocked_by_exclusive"` — no later coupon may apply, even
     another non-stackable one. The tier discount (rule 7) is not a coupon and does not
     count as "a coupon already applied" for this rule.

5. **min_cart check uses the running price.** A coupon's `min_cart_cents` is compared
   against the **running price at the moment the coupon is evaluated** (after the tier
   discount and any earlier applied coupons), not against `base_cents`. If the running
   price is strictly less than `min_cart_cents`, reject with reason `"min_cart"`.

6. **pct value cap.** A single `pct` coupon with `value > 5000` (more than 50.00%) is
   rejected with reason `"pct_too_large"`. This check happens before the coupon's
   discount is computed or applied.

7. **Tier discount.** Before any coupon is evaluated, apply an automatic percentage
   discount based on `customer["tier"]`: `gold` removes 500 basis points (5.00%);
   `silver` removes 250 basis points (2.50%); any other value removes nothing and adds
   no `applied` entry. When a tier discount is applied, prepend `"tier:gold"` or
   `"tier:silver"` to the `applied` list. The tier discount uses the same
   `round_half_up` step rounding (rule 1).

8. **60% total-discount cap.** The total accumulated discount (the sum of every cents
   amount removed so far, **including the tier discount** of rule 7) may never exceed
   `floor(base_cents * 0.60)` cents. Before applying any coupon, compute the cents that
   coupon would remove; if adding it to the running total of removed cents would exceed
   the cap, that coupon is rejected with reason `"cap_exceeded"` and is **not** applied
   (not even partially). Evaluation continues: a later, smaller coupon that still fits
   under the cap may still apply. The tier discount itself is always applied even if it
   alone were to approach the cap (the tier discount is never rejected).

9. **Minimum charge clamp.** The minimum-charge clamp applies to `fixed` coupons only.
   A `pct` coupon (or tier discount) may reduce the running price below 50; only the
   `fixed`-coupon clamp below enforces the 50-cent floor. If applying a `fixed`
   coupon would bring the running price below `50`, clamp the running price to `50`,
   mark the coupon **applied** (clamping is not a rejection), and treat the amount
   actually removed as `(running_price_before - 50)`. **However**, the 60% cap of rule 8
   is evaluated against the coupon's **pre-clamp** removal amount (the full `value` for a
   fixed coupon), not the clamped amount. So a fixed coupon may be rejected by rule 8
   for crossing the cap even though, had it applied, clamping would have removed less.

10. **Duplicate codes.** If a coupon's `code` has already appeared earlier in the
    evaluation order (whether that earlier occurrence was applied or rejected), the
    later occurrence is rejected with reason `"duplicate"`. The first occurrence is
    evaluated normally.

11. **Invalid kind.** A coupon whose `kind` is not exactly `"pct"` or `"fixed"`
    (including missing, empty, or any other string) is rejected with reason
    `"invalid"`. This is decided before rules 5, 6, 8, 9.

12. **Empty cart.** If `cart["items"] == 0`, return immediately: `final_cents ==
    base_cents` (no tier discount, no coupons), `applied == []`, and **every** coupon
    rejected with reason `"empty_cart"` in evaluation order (rule 2 ordering still
    applies). Duplicate/invalid sub-classification is **not** done in this case — every
    coupon, including duplicates and invalid ones, gets `"empty_cart"`.

13. **Per-coupon precedence of rejection reasons.** When a single coupon could be
    rejected for more than one reason, the reason reported is the **first** applicable
    in this fixed priority order: `empty_cart` (rule 12) > `duplicate` (rule 10) >
    `invalid` (rule 11) > `blocked_by_exclusive` (rule 4) > `not_stackable` (rule 4) >
    `pct_too_large` (rule 6) > `min_cart` (rule 5) > `cap_exceeded` (rule 8). Only one
    reason is ever reported per coupon.

14. **`applied` list contents and order.** The `applied` list contains, in application
    order: the tier entry (if any) first, then each applied coupon's `code`. A coupon
    that is clamped (rule 9) still appears in `applied`. The order reflects evaluation
    order (rule 2), so all applied `pct` coupons precede all applied `fixed` coupons.

15. **`rejected` list order.** The `rejected` list lists `(code, reason)` tuples in the
    order each rejection is decided, which is the evaluation order of rule 2. (Under
    rule 12 this is simply every coupon in evaluation order.)

16. **fixed coupon removal accounting.** A `fixed` coupon with `value == v` removes
    `min(v, running_price - 50)` cents from the running price when applied (clamping per
    rule 9), but as stated in rule 9 the cap check (rule 8) uses the full `v`. A `fixed`
    coupon whose `value` is larger than `running_price - 50` is still **applied** (it
    clamps); it is only rejected if it independently fails rule 5, 8, 10, or 11.

17. **Running total of removed cents.** The cap of rule 8 tracks the cumulative
    **pre-clamp** removed cents: the tier discount contributes its actual removed cents;
    each applied `pct` coupon contributes its rounded removal; each applied `fixed`
    coupon contributes its full `value` (pre-clamp), even when clamping later removes
    less from the running price. This running total is the quantity compared against the
    cap.

18. **No coupons / no tier.** With an empty `coupons` list and a non-tier customer and a
    non-empty cart, return `{"final_cents": base_cents, "applied": [], "rejected": []}`.
