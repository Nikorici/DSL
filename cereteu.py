import random
import sys
sys.setrecursionlimit(500000)

# ─────────────────────────────────────────────────────────────────────────────
#  ITERATION COUNTERS
# ─────────────────────────────────────────────────────────────────────────────
iter_merge = [0]
iter_quick = [0]
iter_heap  = [0]
iter_tim   = [0]


# ─────────────────────────────────────────────────────────────────────────────
#  MERGE SORT
# ─────────────────────────────────────────────────────────────────────────────
def _merge(arr, left, mid, right):
    L = arr[left:mid + 1]
    R = arr[mid + 1:right + 1]
    i = j = 0
    k = left
    while i < len(L) and j < len(R):
        iter_merge[0] += 1
        if L[i] <= R[j]:
            arr[k] = L[i]; i += 1
        else:
            arr[k] = R[j]; j += 1
        k += 1
    while i < len(L):
        arr[k] = L[i]; i += 1; k += 1
    while j < len(R):
        arr[k] = R[j]; j += 1; k += 1

def merge_sort(arr, left, right):
    if left >= right:
        return
    iter_merge[0] += 1
    mid = left + (right - left) // 2
    merge_sort(arr, left, mid)
    merge_sort(arr, mid + 1, right)
    _merge(arr, left, mid, right)


# ─────────────────────────────────────────────────────────────────────────────
#  QUICK SORT
# ─────────────────────────────────────────────────────────────────────────────
def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        iter_quick[0] += 1
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def quick_sort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)


# ─────────────────────────────────────────────────────────────────────────────
#  HEAP SORT
# ─────────────────────────────────────────────────────────────────────────────
def heapify(arr, n, i):
    largest = i
    left    = 2 * i + 1
    right   = 2 * i + 2
    if left < n:
        iter_heap[0] += 1
        if arr[left] > arr[largest]:
            largest = left
    if right < n:
        iter_heap[0] += 1
        if arr[right] > arr[largest]:
            largest = right
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

def heap_sort(arr):
    n = len(arr)
    # Build max-heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    # Extract elements one by one
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)


# ─────────────────────────────────────────────────────────────────────────────
#  TIM SORT
# ─────────────────────────────────────────────────────────────────────────────
MIN_MERGE = 32

def _insertion_sort(arr, left, right):
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            iter_tim[0] += 1
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
        iter_tim[0] += 1

def _merge_tim(arr, left, mid, right):
    L = arr[left:mid + 1]
    R = arr[mid + 1:right + 1]
    i = j = 0
    k = left
    while i < len(L) and j < len(R):
        iter_tim[0] += 1
        if L[i] <= R[j]:
            arr[k] = L[i]; i += 1
        else:
            arr[k] = R[j]; j += 1
        k += 1
    while i < len(L):
        arr[k] = L[i]; i += 1; k += 1
    while j < len(R):
        arr[k] = R[j]; j += 1; k += 1

def tim_sort(arr):
    n = len(arr)
    for i in range(0, n, MIN_MERGE):
        _insertion_sort(arr, i, min(i + MIN_MERGE - 1, n - 1))
    size = MIN_MERGE
    while size < n:
        for left in range(0, n, 2 * size):
            mid   = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                _merge_tim(arr, left, mid, right)
        size *= 2


# ─────────────────────────────────────────────────────────────────────────────
#  RUNNER  –  run one algorithm, reset its counter, return iteration count
# ─────────────────────────────────────────────────────────────────────────────
def run(algo_name, data):
    arr = data[:]
    if algo_name == "Merge Sort":
        iter_merge[0] = 0
        merge_sort(arr, 0, len(arr) - 1)
        return iter_merge[0]
    elif algo_name == "Quick Sort":
        iter_quick[0] = 0
        quick_sort(arr, 0, len(arr) - 1)
        return iter_quick[0]
    elif algo_name == "Heap Sort":
        iter_heap[0] = 0
        heap_sort(arr)
        return iter_heap[0]
    elif algo_name == "Tim Sort":
        iter_tim[0] = 0
        tim_sort(arr)
        return iter_tim[0]


# ─────────────────────────────────────────────────────────────────────────────
#  INPUT GENERATORS
# ─────────────────────────────────────────────────────────────────────────────
def make_inputs(n, seed=42):
    rng = random.Random(seed)
    return {
        "Best Case (sorted ascending)":      list(range(1, n + 1)),
        "Average Case (random)":             rng.sample(range(1, n * 10 + 1), n),
        "Worst Case (sorted descending)":    list(range(n, 0, -1)),
        "Nearly Sorted (1% swaps)":          _nearly_sorted(n, pct=0.01, seed=seed),
        "Many Duplicates":                   [rng.randint(1, max(1, n // 10)) for _ in range(n)],
        "All Identical":                     [42] * n,
        "Alternating High-Low":              _alternating(n),
        "Reverse Sorted Blocks (size=10)":   _block_reverse(n, block=10),
    }

def _nearly_sorted(n, pct, seed):
    arr = list(range(1, n + 1))
    rng = random.Random(seed)
    swaps = max(1, int(n * pct))
    for _ in range(swaps):
        i, j = rng.randrange(n), rng.randrange(n)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

def _alternating(n):
    # [n, 1, n-1, 2, n-2, 3, ...]
    lo, hi = 1, n
    out = []
    toggle = True
    while lo <= hi:
        out.append(hi if toggle else lo)
        if toggle: hi -= 1
        else:      lo += 1
        toggle = not toggle
    return out

def _block_reverse(n, block):
    base = list(range(1, n + 1))
    arr = []
    for i in range(0, n, block):
        arr.extend(reversed(base[i:i + block]))
    return arr


# ─────────────────────────────────────────────────────────────────────────────
#  PRINT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
ALGORITHMS = ["Merge Sort", "Quick Sort", "Heap Sort", "Tim Sort"]
COL_W = 14   # column width for algorithm names

def print_header():
    alg_cols = "".join(f"{a:>{COL_W}}" for a in ALGORITHMS)
    print(f"\n{'Case':<38}{alg_cols}")
    print("─" * (38 + COL_W * len(ALGORITHMS)))

def print_row(case_name, counts):
    row = f"{case_name:<38}"
    for c in counts:
        row += f"{c:>{COL_W},}"
    print(row)

def print_section(title):
    print(f"\n{'═' * 94}")
    print(f"  {title}")
    print(f"{'═' * 94}")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    SIZES = [10, 50, 100, 250, 500, 750, 1000, 2000, 5000]

    print("=" * 94)
    print("  SORTING ALGORITHM BENCHMARK  –  Iteration Counts")
    print("  Algorithms: Merge Sort | Quick Sort | Heap Sort | Tim Sort")
    print("=" * 94)

    # ── Per-size breakdown ──────────────────────────────────────────────────
    for n in SIZES:
        print_section(f"n = {n}")
        inputs = make_inputs(n)
        print_header()
        for case_name, data in inputs.items():
            counts = [run(alg, data) for alg in ALGORITHMS]
            print_row(case_name, counts)

    # ── Summary table: best / average / worst across all sizes ──────────────
    print_section("SUMMARY — Best / Average / Worst Cases Only")
    print(f"\n{'n':<8}", end="")
    for alg in ALGORITHMS:
        print(f"{alg:^{COL_W*3}}", end="")
    print()
    print(f"{'':8}", end="")
    for _ in ALGORITHMS:
        print(f"{'Best':>{COL_W}}{'Average':>{COL_W}}{'Worst':>{COL_W}}", end="")
    print()
    print("─" * (8 + COL_W * 3 * len(ALGORITHMS)))

    for n in SIZES:
        rng = random.Random(42)
        cases = {
            "best":  list(range(1, n + 1)),
            "avg":   rng.sample(range(1, n * 10 + 1), n),
            "worst": list(range(n, 0, -1)),
        }
        print(f"{n:<8}", end="")
        for alg in ALGORITHMS:
            for key in ("best", "avg", "worst"):
                c = run(alg, cases[key])
                print(f"{c:>{COL_W},}", end="")
        print()

    # ── Complexity reminder ─────────────────────────────────────────────────
    print(f"\n{'═' * 94}")
    print("  THEORETICAL TIME COMPLEXITY")
    print(f"{'═' * 94}")
    header = f"  {'Algorithm':<16} {'Best':>14} {'Average':>14} {'Worst':>14}  {'Stable':>8}  {'In-Place':>10}"
    print(header)
    print("  " + "─" * 70)
    rows = [
        ("Merge Sort",  "O(n log n)", "O(n log n)", "O(n log n)", "Yes", "No"),
        ("Quick Sort",  "O(n log n)", "O(n log n)", "O(n²)",      "No",  "Yes"),
        ("Heap Sort",   "O(n log n)", "O(n log n)", "O(n log n)", "No",  "Yes"),
        ("Tim Sort",    "O(n)",       "O(n log n)", "O(n log n)", "Yes", "No"),
    ]
    for alg, b, avg, w, stable, inplace in rows:
        print(f"  {alg:<16} {b:>14} {avg:>14} {w:>14}  {stable:>8}  {inplace:>10}")
    print(f"{'═' * 94}\n")


if __name__ == "__main__":
    main()