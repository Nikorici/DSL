from grammar import Grammar


class FiniteAutomaton:
    """
    Represents a Finite Automaton FA = (Q, Σ, δ, q0, F).
    Supports determinism checking, FA-to-grammar conversion,
    NDFA-to-DFA conversion (subset construction), and graphical output.
    """

    def __init__(self, Q, sigma, delta, q0, F):
        """
        Initialize the finite automaton.

        Parameters:
            Q     : set of str  - States
            sigma : set of str  - Input alphabet
            delta : dict        - Transitions {(state, symbol): set of next_states}
            q0    : str         - Initial state
            F     : set of str  - Set of final (accepting) states
        """
        self.Q = Q
        self.sigma = sigma
        self.delta = delta
        self.q0 = q0
        self.F = F

    # ------------------------------------------------------------------
    # Task 3b: Determine whether FA is deterministic or non-deterministic
    # ------------------------------------------------------------------
    def is_deterministic(self):
        """
        A finite automaton is deterministic (DFA) if and only if
        for every (state, symbol) pair there is at most one next state.
        Returns (bool, reason_string).
        """
        for state in self.Q:
            for symbol in self.sigma:
                next_states = self.delta.get((state, symbol), set())
                if len(next_states) > 1:
                    return False, (
                        f"δ({state}, {symbol}) = {{{', '.join(sorted(next_states))}}} "
                        f"— multiple transitions"
                    )
        return True, "Each (state, symbol) pair has at most one transition."

    # ------------------------------------------------------------------
    # Task 3a: Convert FA to Regular Grammar
    # ------------------------------------------------------------------
    def to_regular_grammar(self):
        """
        Convert the finite automaton to an equivalent right-linear
        regular grammar G = (VN, VT, P, S).

        Mapping: each state qi is mapped to a non-terminal symbol.
        - q0 → S  (start symbol)
        - other states → A, B, C, …

        For each transition δ(qi, a) = qj:
            • If qj is NOT final:  Qi → aQj
            • If qj IS final and has outgoing transitions: Qi → aQj | a
            • If qj IS final and has NO outgoing transitions: Qi → a

        Returns:
            (Grammar, dict): grammar object and state-to-nonterminal map
        """
        # Build state → non-terminal mapping
        nt_pool = 'ABCDEFGHIJKLMNOPQRTUVWXYZ'  # S reserved for start
        state_to_nt = {self.q0: 'S'}
        idx = 0
        for state in sorted(self.Q):
            if state not in state_to_nt:
                while idx < len(nt_pool) and nt_pool[idx] == 'S':
                    idx += 1
                state_to_nt[state] = nt_pool[idx]
                idx += 1

        VN = set(state_to_nt.values())
        VT = set(self.sigma)
        S = 'S'
        P = {nt: [] for nt in VN}

        for (state, symbol), next_states in self.delta.items():
            for ns in next_states:
                nt_from = state_to_nt[state]
                nt_to = state_to_nt[ns]

                has_outgoing = any(
                    len(self.delta.get((ns, s), set())) > 0
                    for s in self.sigma
                )

                if ns in self.F:
                    # Terminal production (allows stopping at final state)
                    P[nt_from].append(symbol)
                    # Non-terminal production (allows continuing past final state)
                    if has_outgoing:
                        P[nt_from].append(symbol + nt_to)
                else:
                    P[nt_from].append(symbol + nt_to)

        # Remove duplicate productions
        for nt in P:
            P[nt] = list(dict.fromkeys(P[nt]))

        # Remove non-terminals that have no productions (dead-end symbols)
        active_nts = {nt for nt in VN if P.get(nt, [])}
        active_nts.add(S)
        VN = active_nts
        P = {nt: prods for nt, prods in P.items() if nt in active_nts}

        grammar = Grammar(VN, VT, P, S)
        return grammar, state_to_nt

    # ------------------------------------------------------------------
    # Task 3c: Convert NDFA to DFA (Subset Construction)
    # ------------------------------------------------------------------
    def to_dfa(self):
        """
        Convert a non-deterministic FA to a deterministic FA using
        the subset construction (power-set) algorithm.

        Each DFA state corresponds to a set of NFA states.

        Returns:
            (FiniteAutomaton, dict): DFA automaton and a mapping
                {dfa_state_name: set of nfa states}
        """
        start = frozenset([self.q0])
        dfa_states = set()
        dfa_delta = {}
        worklist = [start]

        while worklist:
            current = worklist.pop(0)
            if current in dfa_states:
                continue
            dfa_states.add(current)

            for symbol in sorted(self.sigma):
                next_set = set()
                for state in current:
                    next_set |= self.delta.get((state, symbol), set())

                if not next_set:
                    continue

                next_frozen = frozenset(next_set)
                dfa_delta[(current, symbol)] = {next_frozen}

                if next_frozen not in dfa_states:
                    worklist.append(next_frozen)

        # Determine final states (any DFA state containing an NFA final state)
        dfa_final = {s for s in dfa_states if s & self.F}

        # Create readable names for DFA states
        sorted_states = sorted(
            dfa_states, key=lambda s: (len(s), tuple(sorted(s)))
        )
        name_map = {}
        for i, state_set in enumerate(sorted_states):
            name_map[state_set] = f"D{i}"

        # Build new DFA with readable names
        new_Q = set(name_map.values())
        new_sigma = set(self.sigma)
        new_delta = {}
        new_q0 = name_map[start]
        new_F = {name_map[s] for s in dfa_final}

        for (state_set, symbol), next_sets in dfa_delta.items():
            for ns in next_sets:
                new_delta[(name_map[state_set], symbol)] = {name_map[ns]}

        # Reverse mapping: DFA state name → set of NFA state names
        reverse_map = {v: set(k) for k, v in name_map.items()}

        dfa = FiniteAutomaton(new_Q, new_sigma, new_delta, new_q0, new_F)
        return dfa, reverse_map

    # ------------------------------------------------------------------
    # String acceptance (works for both NFA and DFA)
    # ------------------------------------------------------------------
    def accepts_string(self, input_string):
        """
        Simulate the automaton on the given input string.
        Uses set-of-states tracking (works for NFA and DFA alike).
        Returns True if the string is accepted.
        """
        current = {self.q0}
        for ch in input_string:
            next_states = set()
            for state in current:
                next_states |= self.delta.get((state, ch), set())
            current = next_states
            if not current:
                return False
        return bool(current & self.F)

    # ------------------------------------------------------------------
    # Task 3d (Bonus): Graphical Representation
    # ------------------------------------------------------------------
    def draw_graph(self, filename='fa_graph', title='Finite Automaton'):
        """
        Render the automaton as a PNG image using graphviz.
        Requires: pip install graphviz  +  Graphviz system package.
        """
        try:
            from graphviz import Digraph
        except ImportError:
            print("[!] graphviz library not found. Install with:  pip install graphviz")
            print("    Also install Graphviz software: https://graphviz.org/download/")
            return None

        dot = Digraph(comment=title)
        dot.attr(rankdir='LR', size='10')
        dot.attr('node', shape='circle', fontsize='12')

        # Invisible start arrow
        dot.node('__start__', '', shape='none', width='0', height='0')

        # Add states
        for state in sorted(self.Q):
            if state in self.F:
                dot.node(state, state, shape='doublecircle')
            else:
                dot.node(state, state)

        dot.edge('__start__', self.q0)

        # Combine transitions with same (src, dst) into a single label
        edge_labels = {}
        for (src, symbol), dst_set in self.delta.items():
            for dst in dst_set:
                key = (src, dst)
                edge_labels.setdefault(key, []).append(symbol)

        for (src, dst), symbols in sorted(edge_labels.items()):
            dot.edge(src, dst, label=', '.join(sorted(symbols)))

        dot.render(filename, format='png', cleanup=True)
        print(f"  Graph saved as {filename}.png")
        return dot

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def __str__(self):
        lines = ["Finite Automaton:"]
        lines.append(f"  Q  = {{{', '.join(sorted(self.Q))}}}")
        lines.append(f"  E  = {{{', '.join(sorted(self.sigma))}}}")
        lines.append(f"  q0 = {self.q0}")
        lines.append(f"  F  = {{{', '.join(sorted(self.F))}}}")
        lines.append("  Transitions:")
        for (state, symbol) in sorted(self.delta.keys()):
            nxt = self.delta[(state, symbol)]
            lines.append(f"    δ({state}, {symbol}) = {{{', '.join(sorted(nxt))}}}")
        return '\n'.join(lines)
