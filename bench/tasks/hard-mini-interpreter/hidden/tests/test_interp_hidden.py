import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from interp import evaluate


def test_int_literal():
    assert evaluate("42") == "42"


def test_string_literal_no_quotes_in_output():
    assert evaluate('"hello world"') == "hello world"


def test_booleans():
    assert evaluate("true") == "true"
    assert evaluate("false") == "false"


def test_string_no_escapes_backslash_is_literal():
    assert evaluate('"a\\b"') == "a\\b"


def test_precedence_chain():
    assert evaluate("1+2*3==7 and not false") == "true"


def test_parens_override_precedence():
    assert evaluate("(1+2)*3") == "9"


def test_unary_minus_binds_tighter_than_plus():
    assert evaluate("-2 + 3") == "1"


def test_unary_not_binds_tighter_than_eq():
    # (not false) == true
    assert evaluate("not false == true") == "true"


def test_let_lower_precedence_than_operators():
    assert evaluate("let x = 1 in x + 2") == "3"


def test_let_shadowing_nested():
    assert evaluate("let x = 1 in let x = 2 in x") == "2"


def test_let_initializer_evaluated_in_outer_scope():
    # inner x = (outer x) + 10 = 11 ; result 11 + (outer x = 1) = 12
    assert evaluate("let x = 1 in (let x = x + 10 in x) + x") == "12"


def test_deep_12_level_let_chain():
    src = "".join("let x%d = %d in " % (k, k) for k in range(12)) + "x0 + x11"
    assert evaluate(src) == "11"


def test_plus_int_addition():
    assert evaluate("2 + 40") == "42"


def test_plus_string_coercion_left():
    assert evaluate('"n=" + -5') == "n=-5"


def test_plus_string_coercion_right():
    assert evaluate('1 + "a"') == "1a"


def test_plus_bool_coercion_to_string():
    assert evaluate('true + "x"') == "truex"


def test_plus_two_bools_is_type_mismatch():
    assert evaluate("true + false") == "error: type mismatch"


def test_floor_division_and_modulo_negative():
    assert evaluate("-7 / 2") == "-4"
    assert evaluate("-7 % 2") == "1"


def test_arith_on_nonint_type_mismatch():
    assert evaluate('"a" * 2') == "error: type mismatch"
    assert evaluate("true - 1") == "error: type mismatch"


def test_division_by_zero():
    assert evaluate("7 / 0") == "error: division by zero"
    assert evaluate("7 % 0") == "error: division by zero"


def test_short_circuit_or_skips_undefined():
    assert evaluate("true or x") == "true"


def test_short_circuit_and_skips_erroring_operand():
    assert evaluate("false and (1 / 0 == 0)") == "false"


def test_short_circuit_right_evaluated_surfaces_error():
    assert evaluate("false or (7 / 0 == 1)") == "error: division by zero"


def test_and_requires_boolean_left_no_truthiness():
    assert evaluate("1 and true") == "error: type mismatch"


def test_or_requires_boolean_right_when_evaluated():
    assert evaluate("false or 1") == "error: type mismatch"


def test_comparison_ints_only():
    assert evaluate("1 < 2") == "true"
    assert evaluate("2 <= 2") == "true"
    assert evaluate('"a" < "b"') == "error: type mismatch"


def test_eq_same_type():
    assert evaluate("1 == 1") == "true"
    assert evaluate('"a" == "a"') == "true"
    assert evaluate("true == false") == "false"
    assert evaluate("1 != 2") == "true"


def test_eq_cross_type_is_error_not_false():
    assert evaluate('1 == "1"') == "error: type mismatch"
    assert evaluate("1 == true") == "error: type mismatch"


def test_undefined_variable_message_includes_name():
    assert evaluate("x") == "error: undefined variable 'x'"
    assert evaluate("let x = 1 in y") == "error: undefined variable 'y'"


def test_first_error_wins_left_to_right():
    assert evaluate("y + (7 / 0)") == "error: undefined variable 'y'"
    assert evaluate("(7 / 0) + y") == "error: division by zero"


def test_syntax_errors():
    assert evaluate("") == "error: syntax error"
    assert evaluate("1 +") == "error: syntax error"
    assert evaluate("(1 + 2") == "error: syntax error"
    assert evaluate("1 2") == "error: syntax error"
    assert evaluate('"abc') == "error: syntax error"
    assert evaluate("let x = in 1") == "error: syntax error"


def test_runtime_error_not_syntax_when_parseable():
    assert evaluate("1 + 1 / 0") == "error: division by zero"
