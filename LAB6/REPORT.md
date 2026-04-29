# Laboratory Work 6: Parser and Abstract Syntax Tree

### Course: Formal Languages & Finite Automata

### Author: Daniel Nicorici

### Group: FAF-243

---

## 1. Introduction

After lexical analysis produces a flat sequence of tokens, the next compiler phase is **parsing** — the process of determining whether that sequence conforms to the language grammar and simultaneously building a structured representation of the program.

The most common structured representation is the **Abstract Syntax Tree (AST)**. Unlike a concrete parse tree that mirrors every grammar production rule verbatim, an AST retains only the semantically significant nodes. Punctuation, parentheses, and other syntactic glue are implicit in the tree structure itself, making the AST compact and easy to traverse by subsequent compilation passes.

This laboratory work extends the lexer from LAB3 with:
1. A `TokenType` enum whose members carry their own regex pattern.
2. A new regex-driven `Lexer` that identifies tokens via `re.finditer`.
3. A set of `ASTNode` dataclasses covering all language constructs.
4. A recursive-descent `Parser` that converts a token stream into an AST.

## 2. Objectives

1. Add a `TokenType` enum with regex patterns for lexical categorisation.
2. Design an AST hierarchy suited to the LAB3 expression language.
3. Implement a recursive-descent parser that builds the AST.
4. Demonstrate the full pipeline on the same sample program used in LAB3.

## 3. Implemented Files

- [LAB6/lexer.py](lexer.py) — `TokenType` enum, `Token` dataclass, `LexerError`, regex-based `Lexer`.
- [LAB6/ast_nodes.py](ast_nodes.py) — `ASTNode` base class and all concrete node dataclasses.
- [LAB6/parser.py](parser.py) — `ParseError`, `Parser` class with full recursive-descent logic.
- [LAB6/main.py](main.py) — CLI that prints the token stream and/or the AST.
- [LAB6/REPORT.md](REPORT.md) — this report.

## 4. Token Types and Regex Patterns

The `TokenType` enum was added to satisfy the requirement that tokens are identified with regular expressions:

| TokenType | Pattern | Examples |
|-----------|---------|---------|
| `COMMENT` | `//[^\n]*\|/\*[\s\S]*?\*/` | `// note`, `/* block */` |
| `NUMBER`  | `\d+(?:\.\d+)?(?:[eE][+-]?\d+)?` | `3.14`, `6.02e23` |
| `STRING`  | `"(?:[^"\\]\|\\\.)*"` | `"hello"`, `"a\n"` |
| `KEYWORD` | `\b(?:let\|print\|if\|else\|sin\|cos\|tan)\b` | `let`, `if`, `sin` |
| `IDENT`   | `[A-Za-z_]\w*` | `x`, `result` |
| `OP`      | `==\|!=\|<=\|>=\|[+\-*/^=<>]` | `+`, `>=`, `==` |
| `PUNCT`   | `[(){},;]` | `(`, `;`, `{` |
| `SKIP`    | `[ \t\r\n]+` | whitespace |
| `EOF`     | — | end of input |

A **master regex** is built by joining all patterns into named alternation groups:

```python
_MASTER = re.compile(
    "|".join(f"(?P<{tt.name}>{tt.value})" for tt in TokenType),
    re.MULTILINE,
)
```

`re.finditer` then scans the source in one pass. The ordering of alternatives matters:
- `COMMENT` before `OP` prevents `//` from matching `/` twice.
- `KEYWORD` before `IDENT` ensures reserved words are not classified as identifiers.
- Multi-character operators (`==`, `>=`, etc.) are anchored at the start of `OP`'s pattern.

## 5. AST Node Hierarchy

All nodes extend the `ASTNode` base class and are implemented as Python `dataclass`es. Each node provides a `pretty(indent)` method for formatted printing.

### Expression nodes

| Node | Fields | Meaning |
|------|--------|---------|
| `NumberLiteral` | `value: str` | Numeric constant |
| `StringLiteral` | `value: str` | String constant (already unescaped) |
| `Identifier` | `name: str` | Variable reference |
| `BinaryOp` | `op, left, right` | Infix operator application |
| `UnaryOp` | `op, operand` | Prefix operator (currently `-`) |
| `FunctionCall` | `name, argument` | Trig function call |

### Statement nodes

| Node | Fields | Meaning |
|------|--------|---------|
| `LetStatement` | `name, value` | Variable declaration |
| `PrintStatement` | `value` | Output |
| `IfStatement` | `condition, then_body, else_body` | Conditional (else optional) |
| `ExprStatement` | `expr` | Standalone expression |
| `Program` | `statements` | Root of the tree |

## 6. Parser Design

The parser follows the **recursive-descent** strategy. Each grammar rule maps to a method. Methods call each other according to operator precedence, which is encoded structurally (higher-precedence operations are called from deeper levels).

### Grammar

```
program      := statement* EOF

statement    := let_stmt | print_stmt | if_stmt | expr_stmt
let_stmt     := 'let' IDENT '=' expr ';'
print_stmt   := 'print' '(' expr ')' ';'
if_stmt      := 'if' expr '{' statement* '}' ('else' '{' statement* '}')?
expr_stmt    := expr ';'

expr         := comparison
comparison   := addition (('==' | '!=' | '<' | '<=' | '>' | '>=') addition)*
addition     := mult (('+' | '-') mult)*
mult         := unary (('*' | '/') unary)*
unary        := '-' unary | power
power        := primary ('^' unary)?
primary      := NUMBER | STRING | func_call | IDENT | '(' expr ')'
func_call    := ('sin' | 'cos' | 'tan') '(' expr ')'
```

### Precedence table (lowest to highest)

| Level | Operators |
|-------|-----------|
| comparison | `==  !=  <  <=  >  >=` |
| addition | `+  -` |
| multiplication | `*  /` |
| unary | `-` (prefix) |
| power | `^` (right-associative) |
| primary | literals, identifiers, calls, `( )` |

Right-associativity of `^` is achieved by calling `_unary` (not `_power`) for the exponent operand, which causes the recursion to continue rightward.

### Error reporting

`ParseError` captures the offending `Token` and formats a message with the token type, value, and source line number:

```
ParseError: Expected (';',) (got IDENT 'x' at line 3)
```

## 7. Full Pipeline Demonstration

### Source program (same as LAB3)

```
// Sample program with trig functions
let x = 3.14;
let y = sin(x) + cos(0.5);
print("result=" + y);
/* block comment */
if y >= 0 { print(y); } else { print(-y); }
```

### Token stream (selected)

```
Token(KEYWORD, 'let', line=2, col=1)
Token(IDENT, 'x', line=2, col=5)
Token(OP, '=', line=2, col=7)
Token(NUMBER, '3.14', line=2, col=9)
Token(PUNCT, ';', line=2, col=13)
...
Token(KEYWORD, 'if', line=6, col=1)
Token(OP, '>=', line=6, col=6)
Token(NUMBER, '0', line=6, col=9)
...
Token(EOF, '', line=7, col=0)
```

### AST output

```
Program
  Let(x)
    Number(3.14)
  Let(y)
    BinaryOp(+)
      Call(sin)
        Ident(x)
      Call(cos)
        Number(0.5)
  Print
    BinaryOp(+)
      String('result=')
      Ident(y)
  If
    condition:
      BinaryOp(>=)
        Ident(y)
        Number(0)
    then:
      Print
        Ident(y)
    else:
      Print
        UnaryOp(-)
          Ident(y)
```

The tree correctly reflects the arithmetic structure (precedence), function calls, string concatenation, and the conditional with both branches.

## 8. How to Run

```bash
# Print both token stream and AST (default)
python3 LAB6/main.py

# Token stream only
python3 LAB6/main.py --tokens

# AST only
python3 LAB6/main.py --ast

# Parse a custom file
python3 LAB6/main.py --file path/to/program.txt
```

## 9. Difficulties and Solutions

1. **Keyword vs identifier ambiguity** — In the master regex, `KEYWORD` must appear before `IDENT`; otherwise a word like `let` would match `IDENT` first. Since Python's `re` alternation picks the first matching group, ordering is sufficient.

2. **Operator ordering** — Multi-character operators (`==`, `!=`, `<=`, `>=`) must be listed before their single-character prefixes (`=`, `<`, `>`) in the `OP` pattern. A simple left-to-right alternation with the longer options first handles this correctly.

3. **Right-associativity for exponentiation** — In a standard left-recursive loop, `^` would become left-associative. To make it right-associative, the right operand of `^` is parsed with `_unary` rather than calling `_power` again, which naturally falls through to another `_power` call.

4. **Unary minus in `print(-y)`** — The `-` inside the argument is a unary operator, not a subtraction. Placing `_unary` above `_power` in the call chain means the parser tries unary before primary, correctly handling `-(y)` and similar forms.

## 10. Complexity

| Phase | Complexity |
|-------|------------|
| Lexing | O(n) — single regex scan over the source |
| Parsing | O(n) — each token is consumed exactly once |
| AST printing | O(k) — proportional to the number of nodes |

## 11. Conclusion

LAB6 extends the LAB3 lexer with a regex-backed `TokenType` enum and adds a complete parsing layer. The recursive-descent parser translates the token stream into a typed AST, correctly handling operator precedence, right-associative exponentiation, unary negation, function calls, string literals, and optional `else` branches. The resulting tree is ready for subsequent compiler stages such as type checking, constant folding, or code generation.
