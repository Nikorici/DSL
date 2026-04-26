import argparse
from copy import deepcopy

from cnf import Grammar, parse_grammar


# Variant 17 grammar (hardcoded)
# G = (VN, VT, P, S)
# VN = {S, A, B, C, D, E}  VT = {a, b}
VARIANT_17_VN = {"S", "A", "B", "C", "D", "E"}
VARIANT_17_VT = {"a", "b"}
VARIANT_17_START = "S"
VARIANT_17_RULES = """\
S -> aA | AC
A -> a | ASC | BC | aD
B -> b | bA
C -> ε | BA
E -> aB
D -> abC
"""


def build_variant_17() -> Grammar:
    return parse_grammar(VARIANT_17_VN, VARIANT_17_VT, VARIANT_17_RULES, VARIANT_17_START)


def run_variant(verbose: bool) -> None:
    print("=" * 60)
    print("  Variant 17 — Chomsky Normal Form Conversion")
    print("=" * 60)

    g = build_variant_17()
    print("\nOriginal grammar:")
    print(g)

    g.normalize_to_cnf(verbose=verbose)

    if not verbose:
        print("\nFinal CNF grammar:")
        print(g)


def run_custom(rules_str: str, vn_str: str, vt_str: str, start: str, verbose: bool) -> None:
    vn = set(vn_str.replace(",", " ").split())
    vt = set(vt_str.replace(",", " ").split())
    g = parse_grammar(vn, vt, rules_str, start)

    print("=" * 60)
    print("  Custom Grammar — Chomsky Normal Form Conversion")
    print("=" * 60)
    print("\nOriginal grammar:")
    print(g)

    g.normalize_to_cnf(verbose=verbose)

    if not verbose:
        print("\nFinal CNF grammar:")
        print(g)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Convert a context-free grammar to Chomsky Normal Form (CNF)"
    )
    p.add_argument(
        "--variant",
        action="store_true",
        default=True,
        help="Run conversion on Variant 17 grammar (default)",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Print grammar after each normalization step",
    )
    # Bonus: custom grammar input
    sub = p.add_subparsers(dest="command")
    custom = sub.add_parser("custom", help="Convert a user-supplied grammar")
    custom.add_argument("--vn", required=True, help='Non-terminals, comma or space separated, e.g. "S A B"')
    custom.add_argument("--vt", required=True, help='Terminals, comma or space separated, e.g. "a b"')
    custom.add_argument("--start", required=True, help="Start symbol")
    custom.add_argument(
        "--rules",
        required=True,
        help=(
            'Productions as a semicolon-separated string. '
            'E.g. "S -> aA | AC; A -> a | BC; B -> b | ε"'
        ),
    )
    custom.add_argument("--verbose", action="store_true", help="Print grammar after each step")
    return p


if __name__ == "__main__":
    args = build_parser().parse_args()
    if args.command == "custom":
        rules_str = args.rules.replace(";", "\n")
        run_custom(rules_str, args.vn, args.vt, args.start, args.verbose)
    else:
        run_variant(args.verbose)
