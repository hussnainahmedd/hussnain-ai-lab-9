# =====================================================================
# CS344L - AI Lab | Week 9 | PART 4 of 8
# Topic : TRUTH TABLES - checking every possible world
# Teacher: Raja Faisal Umar
# Run    : python part4_truth_tables.py
# =====================================================================
# A truth table is the most honest tool in logic: list EVERY possible
# model, work the sentence out in each one, and look at the column.
#
#     all True            -> the sentence is VALID
#     at least one True   -> SATISFIABLE
#     none True           -> UNSATISFIABLE
#
# Two sentences with identical columns are EQUIVALENT: one can always
# be swapped for the other. Part 6 rewrites sentences into a special
# shape using exactly these swaps, so the laws proved here are not
# decoration - they are the tools of the next two parts.
#
# The catch, and it is a big one: n symbols means 2^n rows. Ten
# symbols is a thousand rows, twenty is a million, sixty-four is more
# rows than there are grains of sand on Earth. Part 8 measures it.
# =====================================================================

from part2_syntax import NOT, AND, OR, IMPLIES, IFF, show, symbols_in
from part3_semantics import evaluate


def all_models(names):
    """Every possible True/False combination for these symbol names.

    With 3 names this yields 8 dictionaries, one per row of the table.
    """
    total = 2 ** len(names)
    for i in range(total):
        # bit j of the counter decides the value of symbol j
        yield {n: bool((i >> j) & 1) for j, n in enumerate(names)}


def truth_table(sentence, names=None, title=None):
    """Print the full truth table for one sentence."""
    names = names or sorted(symbols_in(sentence))
    text = show(sentence)
    if title:
        print(f"\n   {title}")
    header = "".join(f"{n:>6}" for n in names)
    print(f"   {header}   {text}")
    print(f"   {'-' * (6 * len(names) + 3 + len(text))}")
    column = []
    for model in all_models(names):
        value = evaluate(sentence, model)
        column.append(value)
        row = "".join(f"{'T' if model[n] else 'F':>6}" for n in names)
        print(f"   {row}   {'T' if value else 'F'}")
    return column


def column_of(sentence, names):
    """Just the result column, with no printing - used for comparing."""
    return [evaluate(sentence, m) for m in all_models(names)]


def classify(sentence):
    """VALID, SATISFIABLE or UNSATISFIABLE."""
    names = sorted(symbols_in(sentence))
    column = column_of(sentence, names)
    if all(column):
        return "VALID"
    if any(column):
        return "SATISFIABLE"
    return "UNSATISFIABLE"


def equivalent(left, right):
    """Do these two sentences have identical truth table columns?"""
    names = sorted(symbols_in(left) | symbols_in(right))
    return column_of(left, names) == column_of(right, names)


if __name__ == "__main__":
    print("PART 4: truth tables")
    print("=" * 66)

    # ---------- A: the five connectives, side by side -----------------
    print("\n[A] All five connectives in one table")
    names = ["A", "B"]
    pieces = [NOT("A"), AND("A", "B"), OR("A", "B"),
              IMPLIES("A", "B"), IFF("A", "B")]
    print(f"\n   {'A':>5}{'B':>5}" +
          "".join(f"{show(p):>12}" for p in pieces))
    print(f"   {'-' * (10 + 12 * len(pieces))}")
    for model in all_models(names):
        row = f"   {'T' if model['A'] else 'F':>5}" \
              f"{'T' if model['B'] else 'F':>5}"
        for p in pieces:
            row += f"{'T' if evaluate(p, model) else 'F':>12}"
        print(row)

    print("\n   Look down the '=>' column. Only ONE row is False: the")
    print("   row where A is true and B is false. Students expect two")
    print("   or three Falses there, and that is the usual mistake.")

    # ---------- B: a full table for a cave rule -----------------------
    print("\n[B] A real rule from the cave")
    rule = IFF("B11", OR("P21", "P12"))
    truth_table(rule, ["B11", "P21", "P12"])
    print("\n   Four rows are True. Those four are the only caves in")
    print("   which this rule holds. The other four are ruled out.")

    # ---------- C: validity, satisfiability, contradiction ------------
    print("\n[C] Three kinds of sentence, decided by the column")
    samples = [
        OR("A", NOT("A")),
        IMPLIES(AND("A", IMPLIES("A", "B")), "B"),
        AND("A", "B"),
        AND("A", NOT("A")),
        IFF("A", NOT("A")),
    ]
    print(f"\n   {'sentence':<34}{'verdict'}")
    for sentence in samples:
        print(f"   {show(sentence):<34}{classify(sentence)}")

    print("\n   The second one is modus ponens written as one sentence:")
    print("   'if A is true and A implies B, then B'. It is VALID, which")
    print("   is exactly what makes it a safe rule of reasoning.")

    # ---------- D: the laws Part 6 will use ---------------------------
    print("\n[D] The rewriting laws - each one proved by its table")
    laws = [
        ("eliminate <=>",
         IFF("A", "B"),
         AND(IMPLIES("A", "B"), IMPLIES("B", "A"))),
        ("eliminate =>",
         IMPLIES("A", "B"),
         OR(NOT("A"), "B")),
        ("double negation",
         NOT(NOT("A")),
         "A"),
        ("De Morgan on and",
         NOT(AND("A", "B")),
         OR(NOT("A"), NOT("B"))),
        ("De Morgan on or",
         NOT(OR("A", "B")),
         AND(NOT("A"), NOT("B"))),
        ("distribute or over and",
         OR("A", AND("B", "C")),
         AND(OR("A", "B"), OR("A", "C"))),
        ("contrapositive",
         IMPLIES("A", "B"),
         IMPLIES(NOT("B"), NOT("A"))),
    ]
    print(f"\n   {'law':<26}{'left':<16}{'right':<26}{'same?'}")
    for label, left, right in laws:
        print(f"   {label:<26}{show(left):<16}{show(right):<26}"
              f"{equivalent(left, right)}")

    print("\n   Every one is True, so every one is a legal swap. These")
    print("   seven lines are the whole toolkit for Part 6.")

    # ---------- E: a law that looks right and is not -------------------
    print("\n[E] Two that look like laws but are not")
    traps = [
        ("converse is NOT the same",
         IMPLIES("A", "B"), IMPLIES("B", "A")),
        ("or does not distribute like that",
         OR("A", AND("B", "C")), OR(AND("A", "B"), "C")),
    ]
    for label, left, right in traps:
        print(f"\n   {label}")
        print(f"      {show(left)}  vs  {show(right)}   "
              f"same? {equivalent(left, right)}")

    print("\n   Always check with a table. A law that is almost right")
    print("   is a bug that survives every test you happen to run.")

    # ---------- F: the cost ------------------------------------------
    print("\n[F] What a truth table costs")
    print(f"\n   {'symbols':>9}{'rows':>28}"
          f"{'time at 1 million rows/sec':>28}")
    for n in (3, 8, 10, 20, 30, 40, 64):
        rows = 2 ** n
        seconds = rows / 1_000_000
        if seconds < 1:
            when = f"{seconds * 1000:.1f} milliseconds"
        elif seconds < 60:
            when = f"{seconds:.1f} seconds"
        elif seconds < 86400:
            when = f"{seconds / 60:.1f} minutes"
        elif seconds < 31_536_000:
            when = f"{seconds / 86400:.1f} days"
        else:
            when = f"{seconds / 31_536_000:,.0f} years"
        print(f"   {n:>9}{rows:>28,}{when:>28}")

    print("\n   Our cave has 8 symbols, so 256 rows - instant.")
    print("   A cave with 64 squares needs 584,942 years, which is")
    print("   longer than our species has existed. And buying a")
    print("   computer a thousand times faster still leaves 585 years.")
    print("   You cannot escape 2^n by buying hardware.")
    print("\n   Truth tables are correct and useless at scale. That is")
    print("   the whole reason resolution exists, in Part 7.")
