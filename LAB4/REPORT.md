# Laboratory Work 4: Regular Expressions

### Course: Formal Languages & Finite Automata

### Author: Daniel Nicorici

### Group: FAF-243

---

## 1. Introduction

Regular expressions are a formal and practical notation used to describe sets of strings (formal languages) using compact patterns. They are widely used in compilers, lexers, validators, search tools, log analysis, and data extraction.

From the automata theory perspective, regular expressions are equivalent in expressive power to finite automata. This means that each regular expression can be transformed into an automaton that accepts the same language, and vice versa.

In this laboratory work, a dynamic regular-expression interpreter was implemented that parses expressions into an internal syntax tree and generates valid words from the represented language.

## 2. Objectives

1. Explain what regular expressions are and where they are used.
2. Implement dynamic generation of valid strings based on input regexes, without hardcoding each expression.
3. Limit unbounded repetition (`*` and `+`) to at most 5 occurrences.
4. Implement a bonus function that shows the processing sequence of a regex.
5. Use the variant assigned by student number.

## 3. Variant Selection

Student number is **17**.
Variant is computed cyclically with:

$$
\text{variant} = ((\text{studentNumber} - 1) \bmod 4) + 1
$$

For student 17:

$$
((17 - 1) \bmod 4) + 1 = 1
$$

So the assigned set is **Variant 1**.

## 4. Implemented Files

- `LAB4/regex_engine.py` - parser, AST model, generator, and bonus trace function.
- `LAB4/main.py` - CLI runner, student-to-variant mapping, and output formatting.
- `LAB4/REPORT.md` - current report.

## 5. Supported Regex Features

The implementation supports:

- Grouping: `( ... )`
- Alternation: `A|B`
- Concatenation: implicit (`AB`)
- Quantifiers:
  - `*` (0 to limit)
  - `+` (1 to limit)
  - `?` (0 or 1)
  - `^n` (exactly `n` repetitions)
- Symbols: any non-meta single character (letters, digits, etc.)

For this lab, the limit for `*` and `+` is configurable and defaults to 5, as required.

## 6. How the Program Works

### 6.1 Tokenization and Parsing

The expression is parsed with a recursive-descent parser into an AST, while whitespace is ignored as a separator.

Main grammar (informal):

1. `expression := term ('|' term)*`
2. `term := factor+`
3. `factor := primary quantifier*`
4. `primary := SYMBOL | '(' expression ')'`
5. `quantifier := '*' | '+' | '?' | '^' NUMBER`

AST node types:

- `Symbol`
- `Concat`
- `Alternate`
- `Repeat`

### 6.2 Generation of Valid Words

Generation is done by recursively traversing the AST:

- `Symbol` -> emit symbol
- `Concat` -> generate each part and join
- `Alternate` -> pick one branch
- `Repeat` -> generate between min/max repetitions

Random generation is repeated until enough unique words are collected.

### 6.3 Bonus: Processing Sequence

Function `explain_processing(...)` provides:

- token list,
- AST string representation,
- one generated sample word,
- ordered generation steps (what branch/repetition was chosen and when symbols were emitted).

This satisfies the bonus requirement to show processing sequence.

## 7. Variant 1 Regexes Used

1. `(a|b)(c|d)E+G?`
2. `P(Q|R|S)T(UV|W|X)*Z+`
3. `1(0|1)*2(3|4)^5 36`

## 8. Example Execution

Command:

```bash
python3 LAB4/main.py --student-number 17 --words 10 --star-limit 5 --trace
```

Program behavior:

- computes Variant 1 from student number,
- generates valid words for each regex,
- prints trace information when `--trace` is provided.

## 9. Difficulties and Solutions

1. **Implicit concatenation parsing**
   - Difficulty: concatenation has no explicit symbol and can be confused with alternation and quantifiers.
   - Solution: parser was split by precedence levels (`expression` > `term` > `factor` > `primary`).

2. **Unbounded quantifiers in generation**
   - Difficulty: `*` and `+` can produce infinitely many strings.
   - Solution: bounded with configurable cap (default 5), exactly matching assignment requirement.

3. **Exact repetition notation from tasks**
   - Difficulty: expressions in the assignment include powers such as `^5`.
   - Solution: implemented postfix `^n` quantifier with integer parsing.

## 10. Complexity

- Parsing complexity: $O(n)$ where $n$ is regex length.
- Single-word generation complexity: proportional to generated output length.
- Multi-word generation complexity: depends on requested count and duplicate-collision retries.

## 11. Conclusion

The laboratory requirements were met through a dynamic regex interpreter that:

- parses complex expressions to AST,
- generates valid words without hardcoded templates,
- enforces max repetition of 5 for `*` and `+`,
- includes a detailed processing sequence function for bonus points.

The implementation is reusable for other regex sets and supports all constructs needed by the assignment variants.
