import argparse
import sys

from lexer import Lexer, LexerError, TokenType
from parser import Parser, ParseError


SAMPLE = (
    "// Sample program with trig functions\n"
    "let x = 3.14;\n"
    "let y = sin(x) + cos(0.5);\n"
    'print("result=" + y);\n'
    "/* block comment */\n"
    "if y >= 0 { print(y); } else { print(-y); }\n"
)


def run_tokens(source: str) -> None:
    print("=== Token Stream ===")
    try:
        for tok in Lexer(source).tokenize():
            print(f"  {tok}")
    except LexerError as e:
        print(f"Lexer error: {e}", file=sys.stderr)
        sys.exit(1)


def run_ast(source: str) -> None:
    print("\n=== Abstract Syntax Tree ===")
    try:
        tree = Parser(source).parse()
        print(tree.pretty())
    except (LexerError, ParseError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Tokenize and parse the LAB3 expression language, producing an AST"
    )
    p.add_argument(
        "--tokens",
        action="store_true",
        help="Print the token stream produced by the lexer",
    )
    p.add_argument(
        "--ast",
        action="store_true",
        help="Print the Abstract Syntax Tree (default when no flag is given)",
    )
    p.add_argument(
        "--file",
        metavar="PATH",
        help="Read source from a file instead of the built-in sample program",
    )
    return p


if __name__ == "__main__":
    args = build_parser().parse_args()

    if args.file:
        with open(args.file) as fh:
            source = fh.read()
    else:
        source = SAMPLE
        print("=== Source Program ===")
        print(source)

    show_all = not args.tokens and not args.ast
    if args.tokens or show_all:
        run_tokens(source)
    if args.ast or show_all:
        run_ast(source)
