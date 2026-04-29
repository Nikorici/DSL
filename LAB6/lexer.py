from __future__ import annotations
import re
from dataclasses import dataclass
from enum import Enum
from typing import Iterator, List


class TokenType(Enum):
    """Every token type paired with the regex pattern that matches it."""

    COMMENT = r"//[^\n]*|/\*[\s\S]*?\*/"
    NUMBER  = r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"
    STRING  = r'"(?:[^"\\]|\\.)*"'
    KEYWORD = r"\b(?:let|print|if|else|sin|cos|tan)\b"
    IDENT   = r"[A-Za-z_]\w*"
    OP      = r"==|!=|<=|>=|[+\-*/^=<>]"
    PUNCT   = r"[(){},;]"
    SKIP    = r"[ \t\r\n]+"
    EOF     = r"$"


# Master regex: each alternative is a named group
_MASTER = re.compile(
    "|".join(f"(?P<{tt.name}>{tt.value})" for tt in TokenType if tt is not TokenType.EOF),
    re.MULTILINE,
)


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, line={self.line}, col={self.column})"


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(f"{message} at line {line}, column {column}")
        self.line = line
        self.column = column


class Lexer:
    """Regex-based lexer for the small expression language from LAB3."""

    def __init__(self, source: str) -> None:
        self.source = source

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        line = 1
        line_start = 0

        for m in _MASTER.finditer(self.source):
            kind_name = m.lastgroup
            value = m.group()
            col = m.start() - line_start + 1

            if kind_name == "SKIP":
                # Track newlines inside whitespace for accurate line/col
                newlines = value.count("\n")
                if newlines:
                    line += newlines
                    line_start = m.start() + value.rfind("\n") + 1
                continue

            if kind_name == "COMMENT":
                newlines = value.count("\n")
                if newlines:
                    line += newlines
                    line_start = m.start() + value.rfind("\n") + 1
                continue

            tt = TokenType[kind_name]

            # Unescape string value
            if tt is TokenType.STRING:
                value = _unescape(value[1:-1], line, col)

            tokens.append(Token(tt, value, line, col))

        # Detect unlexed characters (gaps in matches indicate unknown input)
        prev_end = 0
        for m in _MASTER.finditer(self.source):
            if m.start() > prev_end:
                bad_char = self.source[prev_end]
                ln = self.source[:prev_end].count("\n") + 1
                cl = prev_end - self.source[:prev_end].rfind("\n")
                raise LexerError(f"Unexpected character {bad_char!r}", ln, cl)
            prev_end = m.end()

        tokens.append(Token(TokenType.EOF, "", line, 0))
        return tokens


def _unescape(s: str, line: int, col: int) -> str:
    escapes = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}
    result: List[str] = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            ch = s[i + 1]
            if ch not in escapes:
                raise LexerError(f"Invalid escape \\{ch}", line, col)
            result.append(escapes[ch])
            i += 2
        else:
            result.append(s[i])
            i += 1
    return "".join(result)
