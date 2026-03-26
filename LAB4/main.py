import argparse
from typing import Dict, List

from regex_engine import explain_processing, generate_words_from_regex


VARIANT_REGEXES: Dict[int, List[str]] = {
    1: [
        "(a|b)(c|d)E+G?",
        "P(Q|R|S)T(UV|W|X)*Z+",
        "1(0|1)*2(3|4)^5 36",
    ],
    2: [
        "M?N^2(O|P)^3Q*R+",
        "(X|Y|Z)^38+(9|0)",
        "(H|I)(J|K)L*N?",
    ],
    3: [
        "O(P|Q|R)+2(3|4)",
        "A*B(C|D|E)F(G|H|I)^2",
        "J+K(L|M|N)*O?(P|Q)^3",
    ],
    4: [
        "(S|T)(U|V)W*Y+24",
        "L(M|N)O^3P*Q(2|3)",
        "R*S(T|U|V)W(X|Y|Z)^2",
    ],
}


def variant_from_student_number(student_number: int) -> int:
    return ((student_number - 1) % 4) + 1


def run(student_number: int, words_per_regex: int, star_limit: int, seed: int, show_trace: bool) -> None:
    variant = variant_from_student_number(student_number)
    regexes = VARIANT_REGEXES[variant]

    print(f"Student number: {student_number}")
    print(f"Assigned variant: {variant}")
    print(f"Repetition cap for '*' and '+': {star_limit}")
    print()

    for idx, regex in enumerate(regexes, start=1):
        generated = generate_words_from_regex(
            regex,
            count=words_per_regex,
            star_limit=star_limit,
            seed=seed + idx,
        )

        print(f"Regex {idx}: {regex}")
        print("Generated words:")
        for word in generated:
            print(f"  - {word}")

        if show_trace:
            details = explain_processing(regex, star_limit=star_limit, seed=seed + idx)
            print("Processing trace (bonus):")
            print(f"  Tokens: {details['tokens']}")
            print(f"  AST: {details['ast']}")
            print(f"  Sample word: {details['sample_word']}")
            for step in details["steps"]:
                print(f"  * {step}")

        print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate valid words from a set of regular expressions dynamically"
    )
    parser.add_argument(
        "--student-number",
        type=int,
        default=17,
        help="Student number from the list (default: 17)",
    )
    parser.add_argument(
        "--words",
        type=int,
        default=10,
        help="How many words to generate for each regex",
    )
    parser.add_argument(
        "--star-limit",
        type=int,
        default=5,
        help="Maximum expansion for '*' and '+'",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=17,
        help="Random seed for deterministic output",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Show sequence of regex processing (bonus)",
    )
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    run(
        student_number=args.student_number,
        words_per_regex=args.words,
        star_limit=args.star_limit,
        seed=args.seed,
        show_trace=args.trace,
    )
