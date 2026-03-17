from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(f"{message} at line {line}, column {column}")
        self.line = line
        self.column = column


class Lexer:
    KEYWORDS = {
        "let",
        "print",
        "if",
        "else",
        "sin",
        "cos",
        "tan",
    }

    TWO_CHAR_OPS = {"==", "!=", "<=", ">="}
    ONE_CHAR_OPS = {"+", "-", "*", "/", "^", "=", "<", ">"}
    PUNCT = {"(", ")", "{", "}", ",", ";"}

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current = self.text[self.pos] if self.text else None

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.current is not None:
            self._skip_whitespace_and_comments()
            if self.current is None:
                break

            if self.current.isalpha() or self.current == "_":
                tokens.append(self._read_identifier_or_keyword())
            elif self.current.isdigit():
                tokens.append(self._read_number())
            elif self.current == '"':
                tokens.append(self._read_string())
            else:
                token = self._read_operator_or_punct()
                if token is None:
                    raise LexerError("Unexpected character", self.line, self.column)
                tokens.append(token)

        tokens.append(Token("EOF", "", self.line, self.column))
        return tokens

    def _advance(self) -> None:
        if self.current == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
        self.current = self.text[self.pos] if self.pos < len(self.text) else None

    def _peek(self, offset: int = 1) -> Optional[str]:
        index = self.pos + offset
        if index >= len(self.text):
            return None
        return self.text[index]

    def _skip_whitespace_and_comments(self) -> None:
        while self.current is not None:
            if self.current.isspace():
                self._advance()
                continue

            if self.current == "/" and self._peek() == "/":
                self._advance()
                self._advance()
                while self.current is not None and self.current != "\n":
                    self._advance()
                continue

            if self.current == "/" and self._peek() == "*":
                self._advance()
                self._advance()
                while self.current is not None:
                    if self.current == "*" and self._peek() == "/":
                        self._advance()
                        self._advance()
                        break
                    self._advance()
                else:
                    raise LexerError("Unterminated block comment", self.line, self.column)
                continue

            break

    def _read_identifier_or_keyword(self) -> Token:
        line, column = self.line, self.column
        value = []
        while self.current is not None and (self.current.isalnum() or self.current == "_"):
            value.append(self.current)
            self._advance()
        text = "".join(value)
        token_type = "KEYWORD" if text in self.KEYWORDS else "IDENT"
        return Token(token_type, text, line, column)

    def _read_number(self) -> Token:
        line, column = self.line, self.column
        value = []
        while self.current is not None and self.current.isdigit():
            value.append(self.current)
            self._advance()

        if self.current == "." and (self._peek() or "").isdigit():
            value.append(self.current)
            self._advance()
            while self.current is not None and self.current.isdigit():
                value.append(self.current)
                self._advance()

        if self.current in {"e", "E"}:
            peek = self._peek()
            if peek in {"+", "-"} and (self._peek(2) or "").isdigit():
                value.append(self.current)
                self._advance()
                value.append(self.current)
                self._advance()
            elif (peek or "").isdigit():
                value.append(self.current)
                self._advance()
            else:
                return Token("NUMBER", "".join(value), line, column)

            while self.current is not None and self.current.isdigit():
                value.append(self.current)
                self._advance()

        return Token("NUMBER", "".join(value), line, column)

    def _read_string(self) -> Token:
        line, column = self.line, self.column
        self._advance()
        value = []
        while self.current is not None and self.current != '"':
            if self.current == "\\":
                escape = self._peek()
                if escape is None:
                    raise LexerError("Unterminated string", self.line, self.column)
                value.append(self._translate_escape(escape))
                self._advance()
                self._advance()
                continue
            value.append(self.current)
            self._advance()
        if self.current != '"':
            raise LexerError("Unterminated string", self.line, self.column)
        self._advance()
        return Token("STRING", "".join(value), line, column)

    def _translate_escape(self, char: str) -> str:
        escapes = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            '"': '"',
            "\\": "\\",
        }
        if char not in escapes:
            raise LexerError("Invalid escape sequence", self.line, self.column)
        return escapes[char]

    def _read_operator_or_punct(self) -> Optional[Token]:
        line, column = self.line, self.column
        if self.current is None:
            return None

        two_char = (self.current or "") + (self._peek() or "")
        if two_char in self.TWO_CHAR_OPS:
            self._advance()
            self._advance()
            return Token("OP", two_char, line, column)

        if self.current in self.ONE_CHAR_OPS:
            value = self.current
            self._advance()
            return Token("OP", value, line, column)

        if self.current in self.PUNCT:
            value = self.current
            self._advance()
            return Token("PUNCT", value, line, column)

        return None
