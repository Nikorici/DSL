# Lexer and Scanner

### Course: Formal Languages & Finite Automata

### Author: Daniel Nicorici

### Group: FAF-243

---

## Theory

Lexical analysis transforms a raw stream of characters into a stream of tokens. A token is a pair consisting of a type (keyword, identifier, number, operator, etc.) and the lexeme data needed by later stages. The lexer applies the language rules for splitting and classifying lexemes so that parsing can work with a clean, structured input.

## Objectives

1. Understand lexical analysis and its role in a compiler.
2. Implement a lexer that recognizes multiple token categories.
3. Demonstrate tokenization on a non-trivial input that includes numeric and trigonometric functions.

## Implementation Description

The implementation is written in Python and is located in the LAB3 folder:

- `lexer.py` - Lexer implementation and token definitions.
- `main.py` - Demonstration script that prints the produced tokens.

### Token categories

The lexer recognizes the following token groups:

- KEYWORD: let, print, if, else, sin, cos, tan
- IDENT: user-defined identifiers
- NUMBER: integers and floating-point values, with optional exponent
- STRING: double-quoted strings with escape sequences
- OP: operators like +, -, \*, /, ^, =, ==, !=, <=, >=, <, >
- PUNCT: punctuation like (, ), {, }, ,, ;
- EOF: end-of-input marker

### Lexer behavior

The lexer scans the input left-to-right and produces tokens with line and column metadata. It skips whitespace and supports both single-line (//) and block (/\* \*/) comments. Errors are reported with exact line and column positions.

### Example input and output

Input:

```
let x = 3.14;
let y = sin(x) + cos(0.5);
print("result=" + y);
```

Output (simplified):

```
Token(type='KEYWORD', value='let', line=1, column=1)
Token(type='IDENT', value='x', line=1, column=5)
Token(type='OP', value='=', line=1, column=7)
Token(type='NUMBER', value='3.14', line=1, column=9)
Token(type='PUNCT', value=';', line=1, column=13)
...
Token(type='EOF', value='', line=4, column=1)
```

## Conclusions / Results

The lexer correctly identifies identifiers, keywords, numeric literals (including floats and exponents), strings with escapes, operators, punctuation, and comments. The sample input demonstrates trigonometric functions (sin and cos) and mixed token types, meeting the requirement for a more complex lexer than a basic calculator.

## References

1. A sample of a lexer implementation.
2. Lexical analysis.
