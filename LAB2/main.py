"""
LAB 2 — Variant 17
Determinism in Finite Automata. Conversion from NDFA to DFA. Chomsky Hierarchy.

Course : Formal Languages & Finite Automata
"""

from grammar import Grammar
from finite_automaton import FiniteAutomaton


def separator(title):
    print(f"\n{'=' * 62}")
    print(f"  {title}")
    print('=' * 62)


def safe_print(*args, **kwargs):
    """Print with fallback for characters unsupported by the terminal encoding."""
    import sys
    text = ' '.join(str(a) for a in args)
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        print(text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding), **kwargs)


def main():
    print("=" * 62)
    print("  LAB 2 - Variant 17")
    print("  Determinism in Finite Automata")
    print("  Conversion from NDFA to DFA. Chomsky Hierarchy.")
    print("=" * 62)

    # ---------------------------------------------------------------
    # Define the Finite Automaton for Variant 17
    # ---------------------------------------------------------------
    #   Q  = {q0, q1, q2, q3}
    #   Σ  = {a, b, c}
    #   F  = {q3}
    #   δ(q0, a) = q0      δ(q0, a) = q1   (non-deterministic!)
    #   δ(q1, b) = q1       δ(q1, a) = q2
    #   δ(q2, b) = q3       δ(q2, a) = q0
    # ---------------------------------------------------------------

    Q = {'q0', 'q1', 'q2', 'q3'}
    sigma = {'a', 'b', 'c'}
    F = {'q3'}
    q0 = 'q0'
    delta = {
        ('q0', 'a'): {'q0', 'q1'},   # non-determinism here
        ('q1', 'b'): {'q1'},
        ('q1', 'a'): {'q2'},
        ('q2', 'b'): {'q3'},
        ('q2', 'a'): {'q0'},
    }

    fa = FiniteAutomaton(Q, sigma, delta, q0, F)

    separator("Original Finite Automaton (Variant 17)")
    print(fa)

    # ==================================================================
    # Task 3b — Determine whether FA is deterministic or non-deterministic
    # ==================================================================
    separator("Task 3b: Determinism Check")

    is_det, reason = fa.is_deterministic()
    print(f"\n  Result : {'DFA (Deterministic)' if is_det else 'NDFA (Non-Deterministic)'}")
    print(f"  Reason : {reason}")

    # ==================================================================
    # Task 3a — Convert FA to Regular Grammar
    # ==================================================================
    separator("Task 3a: FA → Regular Grammar Conversion")

    grammar, state_map = fa.to_regular_grammar()
    print("\n  State → Non-terminal mapping:")
    for st in sorted(state_map.keys()):
        print(f"    {st} → {state_map[st]}")
    print()
    print(grammar)

    # ==================================================================
    # Task 2a — Classify grammar based on Chomsky hierarchy
    # ==================================================================
    separator("Task 2a: Chomsky Hierarchy Classification")

    chomsky_type, chomsky_name = grammar.classify_chomsky()
    print(f"\n  The derived grammar is: {chomsky_name}")

    # Additional examples to show the classifier works for other types
    print("\n  --- Additional classification examples ---")

    # Context-Free Grammar example (Type 2)
    cfg = Grammar(
        VN={'S', 'A'},
        VT={'a', 'b'},
        P={
            'S': ['aAb', 'ab'],
            'A': ['aAb', 'ab'],
        },
        S='S'
    )
    _, cfg_name = cfg.classify_chomsky()
    print(f"  G = {{S → aAb | ab, A → aAb | ab}}  →  {cfg_name}")

    # Context-Sensitive Grammar example (Type 1)
    csg = Grammar(
        VN={'S', 'A', 'B'},
        VT={'a', 'b', 'c'},
        P={
            'S':  ['aAB'],
            'A':  ['aAB', 'ab'],
            'AB': ['bBc'],
            'B':  ['bc'],
        },
        S='S'
    )
    _, csg_name = csg.classify_chomsky()
    print(f"  G = {{S → aAB, A → aAB|ab, AB → bBc, B → bc}}  →  {csg_name}")

    # ==================================================================
    # Task 3c — Convert NDFA to DFA (Subset Construction)
    # ==================================================================
    separator("Task 3c: NDFA → DFA Conversion (Subset Construction)")

    dfa, dfa_mapping = fa.to_dfa()

    print("\n  DFA state mapping (DFA state → NFA states):")
    for dfa_st in sorted(dfa_mapping.keys()):
        nfa_sts = ', '.join(sorted(dfa_mapping[dfa_st]))
        is_final = " *" if dfa_st in dfa.F else ""
        is_start = " (start)" if dfa_st == dfa.q0 else ""
        print(f"    {dfa_st} = {{{nfa_sts}}}{is_final}{is_start}")
    print()
    print(dfa)

    # Verify the DFA is deterministic
    is_det_dfa, reason_dfa = dfa.is_deterministic()
    print(f"\n  Verification: The converted FA is "
          f"{'DFA ✓' if is_det_dfa else 'NDFA ✗ (ERROR)'}")

    # ==================================================================
    # String acceptance — compare NFA and DFA
    # ==================================================================
    separator("String Acceptance Tests (NFA vs DFA)")

    test_strings = [
        'aab',       # q0→q1→q2→q3  ✓
        'abab',      # q0→q1→q1→q2→q3  ✓
        'abbab',     # q0→q1→q1→q1→q2→q3  ✓
        'aaab',      # q0→q0→q1→q2→q3  ✓
        'aabaaaab',  # cycle through q0 twice  ✓
        'ab',        # ends in q1 (not final)  ✗
        'b',         # no transition from q0 on b  ✗
        'a',         # ends in {q0,q1}  ✗
        'ba',        # no transition from q0 on b  ✗
        'aabb',      # ends in {q1}  ✗
    ]

    print(f"\n  {'String':<16} {'NFA':>10} {'DFA':>10} {'Match':>8}")
    print(f"  {'-'*16} {'-'*10} {'-'*10} {'-'*8}")
    for s in test_strings:
        nfa_res = fa.accepts_string(s)
        dfa_res = dfa.accepts_string(s)
        match = 'OK' if nfa_res == dfa_res else 'FAIL'
        print(f"  {repr(s):<16} {'Accept' if nfa_res else 'Reject':>10} "
              f"{'Accept' if dfa_res else 'Reject':>10} {match:>8}")

    # Generate some strings from the grammar
    separator("Sample Strings Generated from the Grammar")
    strings = grammar.generate_strings(count=8)
    for i, s in enumerate(strings, 1):
        accepted = fa.accepts_string(s)
        print(f"  {i}. \"{s}\"  — NFA {'accepts' if accepted else 'rejects'}")

    # ==================================================================
    # Task 3d (Bonus) — Graphical Representation
    # ==================================================================
    separator("Task 3d (Bonus): Graphical Representation")
    try:
        fa.draw_graph('ndfa_variant17', 'NDFA - Variant 17')
        dfa.draw_graph('dfa_variant17', 'DFA - Variant 17')
    except Exception as e:
        print(f"  Could not generate graphs: {e}")
        print("  To enable graphical output:")
        print("    pip install graphviz")
        print("    + install Graphviz: https://graphviz.org/download/")


if __name__ == '__main__':
    main()
