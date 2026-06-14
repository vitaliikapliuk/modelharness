"""Reference solution for the mini expression interpreter (SPEC.md)."""


class _Err(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


def _syntax():
    raise _Err("error: syntax error")


# ----------------------------------------------------------------------
# Tokenizer
# ----------------------------------------------------------------------

KEYWORDS = {"true", "false", "let", "in", "and", "or", "not"}


def _is_id_start(c):
    return c.isalpha() and c.isascii() or c == "_"


def _is_id_part(c):
    return (c.isalnum() and c.isascii()) or c == "_"


def tokenize(src):
    toks = []
    i = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c in " \t\r\n":
            i += 1
            continue
        if c == '"':
            j = i + 1
            buf = []
            while j < n and src[j] != '"':
                buf.append(src[j])
                j += 1
            if j >= n:
                _syntax()  # unterminated string
            toks.append(("str", "".join(buf)))
            i = j + 1
            continue
        if c.isdigit():
            j = i
            while j < n and src[j].isdigit():
                j += 1
            toks.append(("int", int(src[i:j])))
            i = j
            continue
        if _is_id_start(c):
            j = i
            while j < n and _is_id_part(src[j]):
                j += 1
            word = src[i:j]
            if word in KEYWORDS:
                toks.append((word, word))
            else:
                toks.append(("name", word))
            i = j
            continue
        # multi-char operators first
        two = src[i : i + 2]
        if two in ("==", "!=", "<=", ">="):
            toks.append((two, two))
            i += 2
            continue
        if c in "+-*/%<>()=":
            toks.append((c, c))
            i += 1
            continue
        _syntax()  # unknown character
    return toks


# ----------------------------------------------------------------------
# Parser  ->  AST of nested tuples
# ----------------------------------------------------------------------


class _Parser:
    def __init__(self, toks):
        self.toks = toks
        self.pos = 0

    def peek(self):
        if self.pos < len(self.toks):
            return self.toks[self.pos]
        return (None, None)

    def next(self):
        t = self.peek()
        self.pos += 1
        return t

    def expect(self, kind):
        t = self.next()
        if t[0] != kind:
            _syntax()
        return t

    def at_end(self):
        return self.pos >= len(self.toks)

    # entry
    def parse(self):
        node = self.expr()
        if not self.at_end():
            _syntax()
        return node

    def expr(self):
        # let or or-expr
        if self.peek()[0] == "let":
            return self.parse_let()
        return self.parse_or()

    def parse_let(self):
        self.expect("let")
        name_tok = self.next()
        if name_tok[0] != "name":
            _syntax()
        self.expect("=")
        init = self.expr()
        self.expect("in")
        body = self.expr()
        return ("let", name_tok[1], init, body)

    def parse_or(self):
        left = self.parse_and()
        while self.peek()[0] == "or":
            self.next()
            right = self.parse_and()
            left = ("or", left, right)
        return left

    def parse_and(self):
        left = self.parse_eq()
        while self.peek()[0] == "and":
            self.next()
            right = self.parse_eq()
            left = ("and", left, right)
        return left

    def parse_eq(self):
        left = self.parse_cmp()
        while self.peek()[0] in ("==", "!="):
            op = self.next()[0]
            right = self.parse_cmp()
            left = (op, left, right)
        return left

    def parse_cmp(self):
        left = self.parse_add()
        while self.peek()[0] in ("<", ">", "<=", ">="):
            op = self.next()[0]
            right = self.parse_add()
            left = (op, left, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek()[0] in ("+", "-"):
            op = self.next()[0]
            right = self.parse_mul()
            left = (op, left, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek()[0] in ("*", "/", "%"):
            op = self.next()[0]
            right = self.parse_unary()
            left = (op, left, right)
        return left

    def parse_unary(self):
        k = self.peek()[0]
        if k == "-":
            self.next()
            return ("neg", self.parse_unary())
        if k == "not":
            self.next()
            return ("not", self.parse_unary())
        return self.parse_atom()

    def parse_atom(self):
        t = self.next()
        k = t[0]
        if k == "int":
            return ("int", t[1])
        if k == "str":
            return ("str", t[1])
        if k == "true":
            return ("bool", True)
        if k == "false":
            return ("bool", False)
        if k == "name":
            return ("var", t[1])
        if k == "(":
            inner = self.expr()
            self.expect(")")
            return inner
        if k == "let":
            # let used as an atom (e.g. inside parens or as an operand)
            self.pos -= 1
            return self.parse_let()
        _syntax()


# ----------------------------------------------------------------------
# Evaluator
# ----------------------------------------------------------------------


def _typename(v):
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    return "str"


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _is_bool(v):
    return isinstance(v, bool)


def _is_str(v):
    return isinstance(v, str)


def _to_str(v):
    if _is_bool(v):
        return "true" if v else "false"
    if _is_int(v):
        return str(v)
    return v


def _eval(node, env):
    kind = node[0]

    if kind == "int":
        return node[1]
    if kind == "str":
        return node[1]
    if kind == "bool":
        return node[1]
    if kind == "var":
        name = node[1]
        if name in env:
            return env[name]
        raise _Err("error: undefined variable '%s'" % name)

    if kind == "let":
        _, name, init, body = node
        val = _eval(init, env)  # outer scope
        new_env = dict(env)
        new_env[name] = val
        return _eval(body, new_env)

    if kind == "neg":
        v = _eval(node[1], env)
        if not _is_int(v):
            raise _Err("error: type mismatch")
        return -v

    if kind == "not":
        v = _eval(node[1], env)
        if not _is_bool(v):
            raise _Err("error: type mismatch")
        return not v

    if kind == "or":
        left = _eval(node[1], env)
        if not _is_bool(left):
            raise _Err("error: type mismatch")
        if left:
            return True
        right = _eval(node[2], env)
        if not _is_bool(right):
            raise _Err("error: type mismatch")
        return right

    if kind == "and":
        left = _eval(node[1], env)
        if not _is_bool(left):
            raise _Err("error: type mismatch")
        if not left:
            return False
        right = _eval(node[2], env)
        if not _is_bool(right):
            raise _Err("error: type mismatch")
        return right

    # remaining binary ops evaluate left then right (rule 15 order)
    if kind in ("==", "!=", "<", ">", "<=", ">=", "+", "-", "*", "/", "%"):
        left = _eval(node[1], env)
        right = _eval(node[2], env)
        return _binop(kind, left, right)

    raise _Err("error: syntax error")


def _binop(op, left, right):
    if op == "+":
        if _is_int(left) and _is_int(right):
            return left + right
        if _is_str(left) or _is_str(right):
            return _to_str(left) + _to_str(right)
        raise _Err("error: type mismatch")

    if op in ("-", "*", "/", "%"):
        if not (_is_int(left) and _is_int(right)):
            raise _Err("error: type mismatch")
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if right == 0:
            raise _Err("error: division by zero")
        if op == "/":
            return left // right
        return left % right

    if op in ("<", ">", "<=", ">="):
        if not (_is_int(left) and _is_int(right)):
            raise _Err("error: type mismatch")
        if op == "<":
            return left < right
        if op == ">":
            return left > right
        if op == "<=":
            return left <= right
        return left >= right

    if op in ("==", "!="):
        if _typename(left) != _typename(right):
            raise _Err("error: type mismatch")
        eq = left == right
        return eq if op == "==" else (not eq)

    raise _Err("error: syntax error")


def evaluate(src: str) -> str:
    try:
        toks = tokenize(src)
        if not toks:
            return "error: syntax error"
        ast = _Parser(toks).parse()
        result = _eval(ast, {})
        return _to_str(result)
    except _Err as e:
        return e.msg
