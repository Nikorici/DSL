# Laboratory Work 3: Lexer and Scanner

### Course: Formal Languages & Finite Automata

### Author: Daniel Nicorici

### Group: FAF-243

---

## 1. Introduction

Lexical analysis is the first phase of compilation. Its purpose is to convert a sequence of characters into a structured sequence of tokens that can be consumed by a parser. Compared to raw text processing, tokenization reduces ambiguity and provides precise source location metadata (line and column), which is essential for diagnostics.

In this laboratory work, a custom lexer was implemented in Python for a small expression-oriented language with variables, trigonometric function calls, conditions, and string output.

## 2. Objectives

1. Understand how a lexer bridges source text and syntax analysis.
2. Implement deterministic tokenization for multiple lexical categories.
3. Support practical language constructs: comments, escaped strings, floating-point numbers, and relational operators.
4. Provide meaningful error reporting with line/column positions.

## 3. Implementation Overview

Project files used in LAB3:

- `lexer.py` - token model, lexer state, scanning logic, and error handling.
- `main.py` - demonstration program and token stream printing.

### 3.1 Data Structures

- `Token` dataclass contains:
  - `type` (token class),
  - `value` (lexeme content),
  - `line` and `column` (source position).
- `LexerError` extends `Exception` and formats messages as: `message at line X, column Y`.

### 3.2 Supported Token Types

- `KEYWORD`: `let`, `print`, `if`, `else`, `sin`, `cos`, `tan`
- `IDENT`: user-defined names (`[A-Za-z_][A-Za-z0-9_]*`)
- `NUMBER`: integer, decimal, and scientific notation (`1`, `3.14`, `6.02e23`, `1e-3`)
- `STRING`: double-quoted literals with escapes (`\n`, `\t`, `\r`, `\"`, `\\`)
- `OP`: operators `+ - * / ^ = == != <= >= < >`
- `PUNCT`: punctuation `( ) { } , ;`
- `EOF`: explicit end-of-input token

### 3.3 Scanning Strategy

The lexer performs a single left-to-right pass over the input and uses helper methods to classify lexemes:

1. Skip whitespace and comments.
2. Read identifier/keyword if current char starts a name.
3. Read number if current char is a digit.
4. Read string if current char is `"`.
5. Otherwise, read operator or punctuation.
6. If no rule matches, raise `LexerError("Unexpected character", line, column)`.

The implementation prioritizes two-character operators (`==`, `!=`, `<=`, `>=`) before one-character operators to avoid incorrect splitting.

### 3.4 Comment and String Handling

- Single-line comments: `// ...` until newline.
- Block comments: `/* ... */` across lines.
- Unterminated block comments trigger an explicit error.
- Strings are parsed character-by-character, with escape translation via `_translate_escape`.
- Invalid escapes or missing closing `"` also trigger lexical errors.

## 4. Demonstration

### 4.1 Input Program

```txt
// Sample program with trig functions
let x = 3.14;
let y = sin(x) + cos(0.5);
print("result=" + y);
/* block comment */
if y >= 0 { print(y); } else { print(-y); }
```

### 4.2 Representative Output Tokens

```txt
Token(type='KEYWORD', value='let', line=2, column=1)
Token(type='IDENT', value='x', line=2, column=5)
Token(type='OP', value='=', line=2, column=7)
Token(type='NUMBER', value='3.14', line=2, column=9)
Token(type='PUNCT', value=';', line=2, column=13)
...
Token(type='KEYWORD', value='if', line=6, column=1)
Token(type='OP', value='>=', line=6, column=6)
...
Token(type='EOF', value='', line=7, column=1)
```

The token stream confirms correct recognition of arithmetic expressions, function calls, string literals, relational conditions, punctuation boundaries, and end-of-file.

## 5. Complexity and Robustness

- Time complexity: $O(n)$, where $n$ is the input length, because each character is processed a constant number of times.
- Space complexity: $O(k)$ for the token list, where $k$ is the number of produced tokens.
- Diagnostics quality: errors include exact line/column, improving debugging speed.

## 6. Results and Conclusions

The implemented lexer satisfies the laboratory requirements and goes beyond minimal tokenization by supporting:

- scientific numeric notation,
- escape-aware string literals,
- both single-line and block comments,
- multi-character operators,
- precise source position tracking.

This work provides a reliable lexical foundation for the next compiler phase (parsing). The generated token stream is deterministic, structured, and suitable for syntax analysis and semantic processing.

## 7. References

1. LLVM Tutorial, _My First Language Frontend with LLVM_. https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html
2. Aho, Lam, Sethi, Ullman, _Compilers: Principles, Techniques, and Tools_, 2nd edition.
3. Lexical analysis overview. https://en.wikipedia.org/wiki/Lexical_analysis
