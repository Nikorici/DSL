import random


class Grammar:
    """
    Represents a formal grammar G = (VN, VT, P, S).
    Supports Chomsky hierarchy classification and string generation.
    """

    def __init__(self, VN, VT, P, S):
        """
        Initialize the grammar.

        Parameters:
            VN : set of str  - Non-terminal symbols
            VT : set of str  - Terminal symbols
            P  : dict        - Productions {lhs: [rhs1, rhs2, ...]}
            S  : str         - Start symbol
        """
        self.VN = VN
        self.VT = VT
        self.P = P
        self.S = S

    def classify_chomsky(self):
        """
        Classify the grammar according to the Chomsky hierarchy.

        Returns:
            tuple (int, str): (type_number, description)
                3 - Regular Grammar
                2 - Context-Free Grammar
                1 - Context-Sensitive Grammar
                0 - Unrestricted Grammar
        """
        if self._is_regular():
            return (3, "Type 3 - Regular Grammar")
        elif self._is_context_free():
            return (2, "Type 2 - Context-Free Grammar")
        elif self._is_context_sensitive():
            return (1, "Type 1 - Context-Sensitive Grammar")
        else:
            return (0, "Type 0 - Unrestricted Grammar")

    def _is_regular(self):
        """
        Check if the grammar is Type 3 (Regular).
        A regular grammar has productions of the form:
          Right-linear: A -> wB  or  A -> w
          Left-linear:  A -> Bw  or  A -> w
        where A, B are non-terminals and w is a string of terminals.
        The grammar must be consistently right-linear or left-linear.
        """
        right_linear = True
        left_linear = True

        for lhs, rhs_list in self.P.items():
            # Left-hand side must be a single non-terminal
            if lhs not in self.VN:
                return False

            for rhs in rhs_list:
                if rhs in ('ε', ''):
                    continue

                symbols = list(rhs)
                terminals = [s for s in symbols if s in self.VT]
                non_terminals = [s for s in symbols if s in self.VN]

                # All symbols must be recognized
                if len(terminals) + len(non_terminals) != len(symbols):
                    return False

                # At most one non-terminal allowed
                if len(non_terminals) > 1:
                    return False

                if len(non_terminals) == 0:
                    # Pure terminal string — valid for both forms
                    continue

                # Exactly one non-terminal: check its position
                nt_pos = next(i for i, s in enumerate(symbols) if s in self.VN)

                if nt_pos == len(symbols) - 1:
                    # Non-terminal at end → right-linear
                    left_linear = False
                elif nt_pos == 0:
                    # Non-terminal at start → left-linear
                    right_linear = False
                else:
                    # Non-terminal in the middle → not regular
                    return False

        return right_linear or left_linear

    def _is_context_free(self):
        """
        Check if the grammar is Type 2 (Context-Free).
        Every production must have a single non-terminal on the left side.
        """
        for lhs in self.P.keys():
            if lhs not in self.VN:
                return False
        return True

    def _is_context_sensitive(self):
        """
        Check if the grammar is Type 1 (Context-Sensitive).
        For every production α → β: |α| <= |β|.
        Exception: S → ε is allowed if S does not appear on any right-hand side.
        """
        for lhs, rhs_list in self.P.items():
            for rhs in rhs_list:
                rhs_len = 0 if rhs in ('ε', '') else len(rhs)
                if rhs_len < len(lhs):
                    # Only S → ε is tolerated
                    if lhs == self.S and rhs in ('ε', ''):
                        # Verify S doesn't appear on any RHS
                        for _, other_rhs_list in self.P.items():
                            for other_rhs in other_rhs_list:
                                if self.S in other_rhs:
                                    return False
                    else:
                        return False
        return True

    def generate_strings(self, count=5, max_steps=100):
        """Generate random strings from the grammar."""
        results = []
        attempts = 0
        while len(results) < count and attempts < count * 20:
            attempts += 1
            s = self._derive(max_steps)
            if s is not None and s not in results:
                results.append(s)
        return results

    def _derive(self, max_steps):
        """Perform a random derivation from the start symbol."""
        current = self.S
        for _ in range(max_steps):
            # Find positions of non-terminals
            nt_positions = [(i, ch) for i, ch in enumerate(current) if ch in self.VN]
            if not nt_positions:
                return current  # Fully derived

            pos, nt = random.choice(nt_positions)
            productions = self.P.get(nt, [])
            if not productions:
                return None

            rhs = random.choice(productions)
            if rhs == 'ε':
                rhs = ''
            current = current[:pos] + rhs + current[pos + 1:]

        # If still has non-terminals, derivation didn't finish
        if any(ch in self.VN for ch in current):
            return None
        return current

    def __str__(self):
        lines = ["Grammar:"]
        lines.append(f"  VN = {{{', '.join(sorted(self.VN))}}}")
        lines.append(f"  VT = {{{', '.join(sorted(self.VT))}}}")
        lines.append(f"  S  = {self.S}")
        lines.append("  Productions:")
        for lhs in sorted(self.P.keys()):
            prods = self.P[lhs]
            if prods:
                lines.append(f"    {lhs} -> {' | '.join(prods)}")
        return '\n'.join(lines)
