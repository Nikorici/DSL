# Laboratory Work 5: Chomsky Normal Form

### Course: Formal Languages & Finite Automata

### Author: Daniel Nicorici

### Group: FAF-243

---

## 1. Introduction

Chomsky Normal Form (CNF) is a canonical representation for context-free grammars where every production rule has one of exactly two forms:

- **A → BC** — a non-terminal produces exactly two non-terminals.
- **A → a** — a non-terminal produces exactly one terminal.

Converting a CFG to CNF is an important theoretical and practical operation: it enables efficient parsing algorithms such as CYK (Cocke–Younger–Kasami), which run in O(n³) time on grammars in CNF. Any context-free grammar (not generating only ε) can be converted to an equivalent CNF grammar through a fixed sequence of normalisation steps.

## 2. Objectives

1. Understand the five steps of CNF normalisation.
2. Implement each step as a distinct, testable method.
3. Apply the algorithm to the Variant 17 grammar.
4. **Bonus:** Accept any user-supplied grammar, not only the assigned variant.

## 3. Variant 17 Grammar

```
G = (VN, VT, P, S)
VN = {S, A, B, C, D, E}
VT = {a, b}

P:
  1.  S → aA        5.  A → BC       9.  C → ε
  2.  S → AC        6.  A → aD       10. C → BA
  3.  A → a         7.  B → b        11. E → aB
  4.  A → ASC       8.  B → bA       12. D → abC
```

## 4. Implemented Files

- [LAB5/cnf.py](cnf.py) — `Grammar` class with the five normalisation steps and the `parse_grammar` helper.
- [LAB5/main.py](main.py) — CLI that runs the variant grammar and optionally accepts a custom grammar.
- [LAB5/REPORT.md](REPORT.md) — this report.

## 5. Normalisation Algorithm

### 5.1 Step 1 — Eliminate ε-productions

**Goal:** remove all rules of the form A → ε.

1. Find all *nullable* non-terminals — those that can derive the empty string either directly (A → ε) or indirectly (every symbol in some right-hand side is itself nullable).
2. For every production that contains at least one nullable symbol, generate all variants obtained by including or excluding each nullable occurrence (every subset of nullable positions). Empty right-hand sides are discarded.
3. The original ε-rules are removed.

For Variant 17, C → ε makes **C** nullable. No other symbol becomes nullable transitively because no production can derive ε after removing C.

After this step, the added productions are:
- `A → ASC` gains companion `A → AS` (C omitted)
- `A → BC` gains companion `A → B` (unit production, handled next)
- `S → AC` gains companion `S → A` (unit production)
- `D → abC` gains companion `D → ab`

### 5.2 Step 2 — Eliminate unit productions (renamings)

**Goal:** remove all rules of the form A → B where B is a single non-terminal.

For each unit production A → B, add all of B's right-hand sides to A's rule set, then remove A → B. Repeat until no unit productions remain.

From Step 1 we have `S → A` and `A → B`. These are expanded:

- `S → A` is replaced by all of A's productions.
- `A → B` is replaced by all of B's productions.

### 5.3 Step 3 — Eliminate inaccessible symbols

**Goal:** remove non-terminals that can never appear in any sentential form derived from the start symbol.

A BFS/DFS from S over the right-hand sides of all reachable productions builds the reachable set. Symbols outside this set, together with all their productions, are deleted.

In Variant 17, **E** appears on no right-hand side of any production reachable from S, so it is removed. **D** is reached via `A → aD`, so it stays.

### 5.4 Step 4 — Eliminate non-productive symbols

**Goal:** remove non-terminals that cannot produce any finite terminal string.

A symbol is *productive* if at least one of its right-hand sides consists entirely of terminals and other productive non-terminals. This is computed iteratively starting from non-terminals that directly produce terminal strings.

After the previous steps, all remaining non-terminals {S, A, B, C, D} are productive (e.g., B → b, A → a, C → BA, D → ab).

### 5.5 Step 5 — Convert to CNF

**Goal:** ensure every rule is either A → BC or A → a.

Two sub-steps:

1. **Terminal replacement:** for every rule of length ≥ 2 that contains a terminal *t*, introduce a fresh non-terminal T_t with the single rule T_t → t, and replace *t* with T_t in the long rule. This leaves only non-terminals in productions of length ≥ 2.

2. **Binarisation:** for every rule A → X₁ X₂ … Xₙ with n > 2, introduce fresh non-terminals to split it into a chain of binary rules:

   ```
   A  → X₁ Y₁
   Y₁ → X₂ Y₂
   ...
   Y_{n-2} → X_{n-1} Xₙ
   ```

   A cache keyed on the tail tuple (`X₂ … Xₙ`) is used so that identical tails reuse the same intermediate non-terminal.

## 6. Worked Example — Variant 17 Step by Step

### After Step 1 (ε-elimination)
```
S -> a A | A C | A
A -> a | A S C | A S | B C | B | a D
B -> b | b A
C -> B A
D -> a b C | a b
E -> a B
```
Nullable: {C}

### After Step 2 (unit productions removed)
```
S -> a A | A C | a | A S C | A S | B C | a D | b | b A
A -> a | A S C | A S | B C | a D | b | b A
B -> b | b A
C -> B A
D -> a b C | a b
E -> a B
```

### After Step 3 (inaccessible removed)
Removed: **{E}**
```
S -> a A | A C | a | A S C | A S | B C | a D | b | b A
A -> a | A S C | A S | B C | a D | b | b A
B -> b | b A
C -> B A
D -> a b C | a b
```

### After Step 4 (non-productive removed)
No symbols removed — all are productive.

### After Step 5 (CNF)
New non-terminals introduced:
- **T0 → a**
- **T1 → b**
- **Y2 → S C** (shared intermediate for the `SC` tail of `ASC`)
- **Y3 → T1 C** (intermediate for `bC` tail of `abC`)

```
S  -> T0 A | A C | a | A Y2 | A S | B C | T0 D | b | T1 A
A  -> a | A Y2 | A S | B C | T0 D | b | T1 A
B  -> b | T1 A
C  -> B A
D  -> T0 Y3 | T0 T1
T0 -> a
T1 -> b
Y2 -> S C
Y3 -> T1 C
```

Every rule is now either A → a or A → BC. ✓

## 7. How to Run

### Variant 17 (default)

```bash
python3 LAB5/main.py
```

With verbose step-by-step output:

```bash
python3 LAB5/main.py --verbose
```

### Bonus: Custom Grammar

```bash
python3 LAB5/main.py custom \
  --vn "S A B" \
  --vt "a b" \
  --start S \
  --rules "S -> A B | ε; A -> a | A B; B -> b" \
  --verbose
```

Each production line uses `->` with `|` separators and `;` between different left-hand sides. Use `ε` for the empty string.

## 8. Design Notes

### Grammar representation

Productions are stored as `Dict[str, List[List[str]]]` — a mapping from each non-terminal name to a list of right-hand sides, where each right-hand side is a list of symbol name strings. This allows multi-character non-terminal names (e.g. `T0`, `Y2`) created during CNF conversion, which would be ambiguous in a flat-string representation.

### Avoiding duplicate intermediate non-terminals

During binarisation, identical right-hand-side tails reuse the same intermediate non-terminal via a dictionary keyed on the tuple of tail symbols. This keeps the grammar minimal and makes the output easier to read.

## 9. Difficulties and Solutions

1. **Nullable subset generation** — generating all combinations of included/excluded nullable positions requires iterating over 2^k subsets. This is fine in practice because grammars have few nullable symbols.

2. **Iterative unit production removal** — a single pass is not enough when replacing A → B introduces new unit productions transitively. The implementation repeats until stable.

3. **Multi-character non-terminal names** — using a list-of-strings representation for right-hand sides (rather than a plain string) avoids ambiguity between single-char and multi-char symbol names.

## 10. Conclusion

The implementation converts any context-free grammar to Chomsky Normal Form through five structured steps encapsulated in the `Grammar` class. For Variant 17, the original 12 productions across 6 non-terminals and 2 terminals are transformed into a strict CNF grammar with 9 non-terminals. The bonus subcommand accepts arbitrary user-supplied grammars, making the tool reusable beyond the assigned variant.
