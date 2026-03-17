from lexer import Lexer, LexerError


def main() -> None:
    sample = (
        "// Sample program with trig functions\n"
        "let x = 3.14;\n"
        "let y = sin(x) + cos(0.5);\n"
        "print(\"result=\" + y);\n"
        "/* block comment */\n"
        "if y >= 0 { print(y); } else { print(-y); }\n"
    )

    try:
        lexer = Lexer(sample)
        for token in lexer.tokenize():
            print(token)
    except LexerError as exc:
        print(f"Lexer error: {exc}")


if __name__ == "__main__":
    main()
