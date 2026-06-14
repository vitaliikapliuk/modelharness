# mini expression interpreter spec

```python
evaluate(src: str) -> str
```

`evaluate` parses and evaluates a single expression in the language below and returns a
string. On any error it returns one of the exact error strings in rule 13. Error
messages must match the spec **byte-for-byte**.

## Values

There are exactly three value types: integer, string, boolean.

## Grammar / tokens

1. **Integer literals**: one or more ASCII digits, optionally preceded by a unary minus
   (see rule 7 for unary). A bare token of digits is a non-negative integer. There are no
   floats.

2. **String literals**: a double-quote `"`, then zero or more characters that are not a
   double quote, then a closing double quote. There are **no escape sequences** — a
   backslash is an ordinary character and `"` always ends the string.

3. **Booleans**: the bare words `true` and `false`.

4. **Variables**: an identifier is an ASCII letter or underscore followed by zero or more
   ASCII letters, digits, or underscores. The words `true`, `false`, `let`, `in`, `and`,
   `or`, `not` are **keywords** and are never variable names.

5. **Whitespace** (spaces, tabs, newlines) separates tokens and is otherwise ignored.

## let bindings

6. `let NAME = EXPR1 in EXPR2` binds `NAME` to the value of `EXPR1`, then evaluates
   `EXPR2` with that binding in scope. Binding is **lexically scoped**; the binding is
   visible only within `EXPR2`. **Shadowing is allowed**: an inner `let` of the same name
   hides the outer binding within its own body. `EXPR1` is evaluated in the **outer**
   scope (the name being bound is not yet in scope while evaluating its own initializer).
   `let` has lower precedence than every operator: `let x = 1 in x + 2` parses as
   `let x = 1 in (x + 2)`.

## Operators and precedence

7. Operators, from **lowest** to **highest** precedence:

   1. `or`               (binary, left-associative, short-circuit — rule 9)
   2. `and`              (binary, left-associative, short-circuit — rule 9)
   3. `==`  `!=`         (binary, left-associative — rule 11)
   4. `<`  `>`  `<=`  `>=`  (binary, left-associative — rule 10)
   5. `+`  `-`           (binary, left-associative — rules 8, 12)
   6. `*`  `/`  `%`      (binary, left-associative — rules 12, 14)
   7. unary `-`, unary `not`  (prefix, right-associative — rule 7-unary)

   Parentheses `( EXPR )` override precedence.

   **unary**: `-EXPR` negates an integer (error if `EXPR` is not an integer). `not EXPR`
   logically negates a boolean (error if `EXPR` is not a boolean). Unary binds tighter
   than every binary operator, so `-2 + 3` is `(-2) + 3 == 1` and `not a == b` is
   `(not a) == b`.

## `+` and arithmetic typing

8. **`+`**: if **both** operands are integers, integer addition. If **either** operand is
   a string, the other operand is converted to a string and the two are concatenated:
   an integer converts to its decimal representation (e.g. `-5` -> `"-5"`), a boolean
   converts to `"true"` / `"false"`, a string is itself. If neither operand is an integer
   and neither is a string (e.g. `true + false`), it is a type mismatch error.

12. `-`, `*`, `/`, `%` require **both** operands to be integers; otherwise type mismatch.
    `/` is integer division and `%` is the remainder. Use Python's floor semantics for
    both (`-7 / 2 == -4`, `-7 % 2 == 1`).

14. `/` or `%` with a right operand of `0` is a division-by-zero error (rule 13). The
    division-by-zero check happens only after both operands are known to be integers; if
    the right operand is a non-integer it is a type mismatch, not division by zero.

## Boolean operators

9. `and` and `or` are **short-circuit** and require booleans:
    - `or`: evaluate the left operand. It must be a boolean, else type mismatch. If it is
      `true`, the result is `true` and the right operand is **not evaluated**. If it is
      `false`, evaluate the right operand; it must be a boolean, else type mismatch; the
      result is the right operand.
    - `and`: evaluate the left operand. It must be a boolean, else type mismatch. If it is
      `false`, the result is `false` and the right operand is **not evaluated**. If it is
      `true`, evaluate the right operand; it must be a boolean, else type mismatch; the
      result is the right operand.
    - There is **no truthiness**: a non-boolean operand that is actually evaluated is a
      type mismatch. An operand that is **not** evaluated (short-circuited away) is never
      type-checked and never has its errors surfaced — even if it references an undefined
      variable or would divide by zero.

## Comparisons

10. `<`, `>`, `<=`, `>=` require **both** operands to be integers; otherwise type
    mismatch. They produce booleans.

11. `==` and `!=` require both operands to be the **same** type (both int, both string, or
    both boolean). Same-type comparison produces a boolean by value equality (`==`) or
    inequality (`!=`). **Cross-type** comparison (e.g. `1 == "1"`, `1 == true`) is a type
    mismatch error — it is **not** `false`.

## Errors

13. Errors return EXACTLY one of these strings (and nothing else):
    - `error: undefined variable 'NAME'` — reading a variable not in scope; `NAME` is the
      variable's identifier.
    - `error: type mismatch` — any operand-type violation described above.
    - `error: division by zero` — rule 14.
    - `error: syntax error` — the input is not a single well-formed expression (empty
      input, leftover tokens, unbalanced parentheses, a missing operand, an unterminated
      string, a malformed `let`, etc.).

15. **First error wins.** Evaluation proceeds left-to-right; the first error encountered
    in evaluation order is the one returned. (Syntax errors are detected during parsing,
    before any evaluation, so a syntactically invalid program always returns
    `error: syntax error` regardless of what runtime errors it might also contain.)

## Result formatting

16. A successful result is formatted as a string:
    - integer: its decimal representation (e.g. `42`, `-7`).
    - string: its characters **without** surrounding quotes.
    - boolean: `true` or `false`.
