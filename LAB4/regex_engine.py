from __future__ import annotations

from dataclasses import dataclass
import random
from typing import List, Optional, Tuple


META_CHARS = {"(", ")", "|", "*", "+", "?", "^"}


class RegexParseError(Exception):
    pass


@dataclass(frozen=True)
class Node:
    pass


@dataclass(frozen=True)
class Symbol(Node):
    value: str


@dataclass(frozen=True)
class Concat(Node):
    parts: Tuple[Node, ...]


@dataclass(frozen=True)
class Alternate(Node):
    options: Tuple[Node, ...]


@dataclass(frozen=True)
class Repeat(Node):
    node: Node
    min_times: int
    max_times: Optional[int]


def _node_to_text(node: Node) -> str:
    if isinstance(node, Symbol):
        return node.value
    if isinstance(node, Concat):
        return "Concat(" + ", ".join(_node_to_text(part) for part in node.parts) + ")"
    if isinstance(node, Alternate):
        return "Alt(" + " | ".join(_node_to_text(option) for option in node.options) + ")"
    if isinstance(node, Repeat):
        upper = "inf" if node.max_times is None else str(node.max_times)
        return f"Repeat({_node_to_text(node.node)}, {node.min_times}, {upper})"
    raise TypeError(f"Unsupported AST node type: {type(node)!r}")


class RegexParser:
    def __init__(self, text: str, star_limit: int = 5) -> None:
        self.text = text
        self.star_limit = star_limit
        self.index = 0
        self.source = text

    def parse(self) -> Node:
        if not self.source:
            raise RegexParseError("Regular expression cannot be empty")
        node = self._parse_expression()
        if self._peek() is not None:
            raise RegexParseError(
                f"Unexpected character '{self._peek()}' at position {self.index}"
            )
        return node

    def tokenized(self) -> List[str]:
        tokens: List[str] = []
        i = 0
        while i < len(self.source):
            ch = self.source[i]
            if ch.isspace():
                i += 1
                continue
            if ch in META_CHARS:
                if ch == "^":
                    j = i + 1
                    while j < len(self.source) and self.source[j].isspace():
                        j += 1
                    if j >= len(self.source) or not self.source[j].isdigit():
                        raise RegexParseError("'^' must be followed by an integer")
                    while j < len(self.source) and self.source[j].isdigit():
                        j += 1
                    tokens.append("^" + self.source[i + 1:j].strip())
                    i = j
                    continue
                tokens.append(ch)
                i += 1
                continue
            tokens.append(ch)
            i += 1
        return tokens

    def _parse_expression(self) -> Node:
        terms = [self._parse_term()]
        while self._peek() == "|":
            self._consume("|")
            terms.append(self._parse_term())
        if len(terms) == 1:
            return terms[0]
        return Alternate(tuple(terms))

    def _parse_term(self) -> Node:
        factors: List[Node] = []
        while True:
            ch = self._peek()
            if ch is None or ch in ")|":
                break
            factors.append(self._parse_factor())

        if not factors:
            return Symbol("")
        if len(factors) == 1:
            return factors[0]
        return Concat(tuple(factors))

    def _parse_factor(self) -> Node:
        base = self._parse_primary()
        while True:
            ch = self._peek()
            if ch == "*":
                self._consume("*")
                base = Repeat(base, 0, self.star_limit)
            elif ch == "+":
                self._consume("+")
                base = Repeat(base, 1, self.star_limit)
            elif ch == "?":
                self._consume("?")
                base = Repeat(base, 0, 1)
            elif ch == "^":
                self._consume("^")
                times = self._read_number()
                base = Repeat(base, times, times)
            else:
                break
        return base

    def _parse_primary(self) -> Node:
        ch = self._peek()
        if ch is None:
            raise RegexParseError("Unexpected end of expression")

        if ch == "(":
            self._consume("(")
            node = self._parse_expression()
            if self._peek() != ")":
                raise RegexParseError("Missing closing ')' in expression")
            self._consume(")")
            return node

        if ch in META_CHARS:
            raise RegexParseError(f"Unexpected token '{ch}' at position {self.index}")

        self.index += 1
        return Symbol(ch)

    def _peek(self) -> Optional[str]:
        self._skip_spaces()
        if self.index >= len(self.source):
            return None
        return self.source[self.index]

    def _skip_spaces(self) -> None:
        while self.index < len(self.source) and self.source[self.index].isspace():
            self.index += 1

    def _consume(self, expected: str) -> None:
        current = self._peek()
        if current != expected:
            raise RegexParseError(
                f"Expected '{expected}' but found '{current}' at position {self.index}"
            )
        self.index += 1

    def _read_number(self) -> int:
        self._skip_spaces()
        start = self.index
        while self.index < len(self.source) and self.source[self.index].isdigit():
            self.index += 1
        raw = self.source[start:self.index]
        if not raw:
            raise RegexParseError("Expected integer after '^'")
        return int(raw)


def parse_regex(regex: str, star_limit: int = 5) -> Node:
    parser = RegexParser(regex, star_limit=star_limit)
    return parser.parse()


def generate_word(
    node: Node,
    rng: random.Random,
    star_limit: int = 5,
    trace: Optional[List[str]] = None,
) -> str:
    if isinstance(node, Symbol):
        if trace is not None:
            trace.append(f"Emit symbol '{node.value}'")
        return node.value

    if isinstance(node, Concat):
        if trace is not None:
            trace.append("Process concatenation")
        return "".join(generate_word(part, rng, star_limit, trace) for part in node.parts)

    if isinstance(node, Alternate):
        choice = rng.choice(node.options)
        if trace is not None:
            trace.append(f"Choose branch: {_node_to_text(choice)}")
        return generate_word(choice, rng, star_limit, trace)

    if isinstance(node, Repeat):
        upper = star_limit if node.max_times is None else node.max_times
        times = rng.randint(node.min_times, upper)
        if trace is not None:
            trace.append(f"Repeat {_node_to_text(node.node)} {times} time(s)")
        return "".join(generate_word(node.node, rng, star_limit, trace) for _ in range(times))

    raise TypeError(f"Unsupported AST node type: {type(node)!r}")


def generate_words_from_regex(
    regex: str,
    count: int,
    star_limit: int = 5,
    seed: Optional[int] = None,
) -> List[str]:
    ast = parse_regex(regex, star_limit=star_limit)
    rng = random.Random(seed)
    unique: set[str] = set()

    max_tries = max(50, count * 40)
    tries = 0
    while len(unique) < count and tries < max_tries:
        unique.add(generate_word(ast, rng, star_limit=star_limit))
        tries += 1

    return sorted(unique)


def explain_processing(
    regex: str,
    star_limit: int = 5,
    seed: int = 17,
) -> dict:
    parser = RegexParser(regex, star_limit=star_limit)
    tokens = parser.tokenized()
    ast = parser.parse()

    trace: List[str] = ["Tokenization complete", "Parsing complete"]
    rng = random.Random(seed)
    word = generate_word(ast, rng, star_limit=star_limit, trace=trace)

    return {
        "regex": regex,
        "tokens": tokens,
        "ast": _node_to_text(ast),
        "sample_word": word,
        "steps": trace,
    }
