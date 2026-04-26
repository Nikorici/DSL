from __future__ import annotations
from typing import Dict, List, Set, Tuple

Productions = Dict[str, List[List[str]]]


class Grammar:
    """Context-free grammar G = (VN, VT, P, S) with CNF normalization."""

    def __init__(self, vn: Set[str], vt: Set[str], productions: Productions, start: str) -> None:
        self.vn: Set[str] = set(vn)
        self.vt: Set[str] = set(vt)
        self.productions: Productions = {k: [list(r) for r in v] for k, v in productions.items()}
        self.start = start
        self._counter = 0

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _new_nt(self, prefix: str) -> str:
        while True:
            name = f"{prefix}{self._counter}"
            self._counter += 1
            if name not in self.vn and name not in self.vt:
                self.vn.add(name)
                return name

    @staticmethod
    def _rhs_str(rhs: List[str]) -> str:
        return "ε" if not rhs else " ".join(rhs)

    def __str__(self) -> str:
        lines = [
            f"  VN = {{{', '.join(sorted(self.vn))}}}",
            f"  VT = {{{', '.join(sorted(self.vt))}}}",
            f"  S  = {self.start}",
            "  Productions:",
        ]
        for lhs in sorted(self.productions):
            alts = " | ".join(self._rhs_str(r) for r in self.productions[lhs])
            lines.append(f"    {lhs} -> {alts}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Step 1 — eliminate ε-productions
    # ------------------------------------------------------------------

    def eliminate_epsilon(self) -> Set[str]:
        """Remove all ε-productions. Returns the set of nullable non-terminals."""
        nullable: Set[str] = set()
        for lhs, rhs_list in self.productions.items():
            for rhs in rhs_list:
                if not rhs or rhs == ["ε"]:
                    nullable.add(lhs)

        changed = True
        while changed:
            changed = False
            for lhs, rhs_list in self.productions.items():
                if lhs in nullable:
                    continue
                for rhs in rhs_list:
                    if rhs and rhs != ["ε"] and all(s in nullable for s in rhs):
                        nullable.add(lhs)
                        changed = True
                        break

        new_productions: Productions = {}
        for lhs, rhs_list in self.productions.items():
            seen: Set[Tuple[str, ...]] = set()
            new_list: List[List[str]] = []
            for rhs in rhs_list:
                if not rhs or rhs == ["ε"]:
                    continue
                null_pos = [i for i, s in enumerate(rhs) if s in nullable]
                for mask in range(1 << len(null_pos)):
                    excluded = {null_pos[bit] for bit in range(len(null_pos)) if (mask >> bit) & 1}
                    candidate = [s for i, s in enumerate(rhs) if i not in excluded]
                    if candidate:
                        key = tuple(candidate)
                        if key not in seen:
                            seen.add(key)
                            new_list.append(candidate)
            new_productions[lhs] = new_list

        self.productions = new_productions
        return nullable

    # ------------------------------------------------------------------
    # Step 2 — eliminate unit productions (renamings)
    # ------------------------------------------------------------------

    def eliminate_renamings(self) -> None:
        """Remove all unit productions A -> B where B is a non-terminal."""
        changed = True
        while changed:
            changed = False
            for lhs in list(self.productions):
                rhs_list = self.productions[lhs]
                units = [r for r in rhs_list if len(r) == 1 and r[0] in self.vn]
                if not units:
                    continue
                for unit in units:
                    rhs_list.remove(unit)
                    changed = True
                    target = unit[0]
                    for expansion in self.productions.get(target, []):
                        if expansion not in rhs_list:
                            rhs_list.append(list(expansion))

    # ------------------------------------------------------------------
    # Step 3 — eliminate inaccessible symbols
    # ------------------------------------------------------------------

    def eliminate_inaccessible(self) -> Set[str]:
        """Remove non-terminals unreachable from the start symbol. Returns removed set."""
        reachable: Set[str] = {self.start}
        changed = True
        while changed:
            changed = False
            for lhs in list(reachable):
                for rhs in self.productions.get(lhs, []):
                    for sym in rhs:
                        if sym in self.vn and sym not in reachable:
                            reachable.add(sym)
                            changed = True

        removed = self.vn - reachable
        self.vn = reachable
        self.productions = {k: v for k, v in self.productions.items() if k in reachable}
        return removed

    # ------------------------------------------------------------------
    # Step 4 — eliminate non-productive symbols
    # ------------------------------------------------------------------

    def eliminate_nonproductive(self) -> Set[str]:
        """Remove non-terminals that can never produce a terminal string. Returns removed set."""
        productive: Set[str] = set()
        changed = True
        while changed:
            changed = False
            for lhs, rhs_list in self.productions.items():
                if lhs in productive:
                    continue
                for rhs in rhs_list:
                    if all(s in self.vt or s in productive for s in rhs):
                        productive.add(lhs)
                        changed = True
                        break

        removed = self.vn - productive
        self.vn = productive
        new_productions: Productions = {}
        for lhs in productive:
            valid = [r for r in self.productions.get(lhs, [])
                     if all(s in self.vt or s in productive for s in r)]
            if valid:
                new_productions[lhs] = valid
        self.productions = new_productions
        return removed

    # ------------------------------------------------------------------
    # Step 5 — convert to Chomsky Normal Form
    # ------------------------------------------------------------------

    def to_cnf(self) -> None:
        """Convert the grammar to strict CNF: every rule is A->BC or A->a."""
        terminal_nt: Dict[str, str] = {}

        def term_nt(t: str) -> str:
            if t not in terminal_nt:
                nt = self._new_nt("T")
                terminal_nt[t] = nt
                self.productions[nt] = [[t]]
            return terminal_nt[t]

        # Replace terminals in rules of length >= 2
        for lhs, rhs_list in list(self.productions.items()):
            new_list = []
            for rhs in rhs_list:
                if len(rhs) >= 2:
                    new_list.append([term_nt(s) if s in self.vt else s for s in rhs])
                else:
                    new_list.append(list(rhs))
            self.productions[lhs] = new_list

        # Binarize rules of length > 2 using shared intermediate non-terminals
        pair_cache: Dict[Tuple[str, ...], str] = {}

        def binarize(rhs: List[str]) -> List[str]:
            if len(rhs) <= 2:
                return rhs
            tail = tuple(rhs[1:])
            if tail not in pair_cache:
                nt = self._new_nt("Y")
                pair_cache[tail] = nt
                self.productions[nt] = [binarize(list(tail))]
            return [rhs[0], pair_cache[tail]]

        for lhs in list(self.productions):
            self.productions[lhs] = [binarize(rhs) for rhs in self.productions[lhs]]

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def normalize_to_cnf(self, verbose: bool = False) -> List[Tuple[str, str, str]]:
        """
        Run all 5 normalization steps and return a log of (step_title, detail, grammar_snapshot).
        If verbose=True, also prints each step.
        """
        log: List[Tuple[str, str, str]] = []

        def record(title: str, detail: str = "") -> None:
            snapshot = str(self)
            log.append((title, detail, snapshot))
            if verbose:
                print(f"\n{'=' * 60}")
                print(f"  {title}")
                if detail:
                    print(f"  {detail}")
                print("=" * 60)
                print(snapshot)

        nullable = self.eliminate_epsilon()
        record("Step 1: Eliminated ε-productions",
               f"Nullable variables: {{{', '.join(sorted(nullable))}}}")

        self.eliminate_renamings()
        record("Step 2: Eliminated unit productions (renamings)")

        inaccessible = self.eliminate_inaccessible()
        detail = f"Removed inaccessible: {{{', '.join(sorted(inaccessible))}}}" if inaccessible else "No inaccessible symbols"
        record("Step 3: Eliminated inaccessible symbols", detail)

        nonproductive = self.eliminate_nonproductive()
        detail = f"Removed non-productive: {{{', '.join(sorted(nonproductive))}}}" if nonproductive else "No non-productive symbols"
        record("Step 4: Eliminated non-productive symbols", detail)

        self.to_cnf()
        record("Step 5: Chomsky Normal Form obtained")

        return log


# ------------------------------------------------------------------
# Convenience: parse a compact string grammar into the Productions dict
# ------------------------------------------------------------------

def parse_grammar(vn: Set[str], vt: Set[str], rules_str: str, start: str) -> Grammar:
    """
    Parse a grammar from a multi-line string.
    Each line: "LHS -> alt1 | alt2 | ..." where each alt is space-separated symbols.
    Single-char symbols are split automatically when no spaces are present.
    Example: "S -> aA | AC"  or  "S -> a A | A C"
    """
    productions: Productions = {}
    for line in rules_str.strip().splitlines():
        line = line.strip()
        if not line or "->" not in line:
            continue
        lhs, rhs_part = line.split("->", 1)
        lhs = lhs.strip()
        alts = []
        for alt in rhs_part.split("|"):
            alt = alt.strip()
            if " " in alt:
                symbols = alt.split()
            else:
                symbols = list(alt) if alt != "ε" else []
            alts.append(symbols)
        if lhs in productions:
            productions[lhs].extend(alts)
        else:
            productions[lhs] = alts
    return Grammar(vn, vt, productions, start)
