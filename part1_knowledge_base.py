# =====================================================================
# CS344L - AI Lab | Week 9 | PART 1 of 8
# Topic : WHY AN AGENT NEEDS TO REASON, NOT JUST REACT
# Teacher: Raja Faisal Umar
# Run    : python part1_knowledge_base.py
# =====================================================================
# Weeks 3 to 8 were all SEARCH. The agent knew the whole map, or the
# whole board, and looked for a path or an answer inside it.
#
# This week the agent is BLIND. It stands in a dark cave and can only
# feel what is in the square it is standing on. It must work out what
# is in the squares it has never seen - from rules it was told, plus
# what it has felt so far.
#
# That is a KNOWLEDGE-BASED AGENT:
#
#     KNOWLEDGE BASE  - a list of sentences the agent believes
#     TELL            - add a new sentence to the knowledge base
#     ASK             - ask whether something FOLLOWS from it
#
# This file sets up the cave and shows, in plain Python, why a
# "reacting" agent cannot survive in it. Parts 2 to 8 then build the
# logic machinery that lets a reasoning agent do it properly.
# =====================================================================

# ---------------------------------------------------------------------
# THE CAVE: 3 columns wide, 2 rows tall. Square [c,r].
#
#        +--------+--------+--------+
#   r=2  | [1,2]  | [2,2]  | [3,2]  |
#        +--------+--------+--------+
#   r=1  | [1,1]  | [2,1]  | [3,1]  |
#        +--------+--------+--------+
#          c=1      c=2      c=3
#
# Some squares hold a PIT. Fall in one and the agent is finished.
# The agent cannot see a pit. But a pit makes a BREEZE in every
# square next to it (up, down, left, right - not diagonally).
#
# So the agent feels a breeze and must REASON backwards:
#     "there is a breeze here, so one of my neighbours has a pit"
# ---------------------------------------------------------------------

COLUMNS, ROWS = 3, 2

SQUARES = [(c, r) for r in range(1, ROWS + 1) for c in range(1, COLUMNS + 1)]


def name(prefix, square):
    """Turn ('P', (2,1)) into the symbol name 'P21'."""
    c, r = square
    return f"{prefix}{c}{r}"


def neighbours(square):
    """The squares directly up, down, left and right - never diagonal."""
    c, r = square
    around = [(c - 1, r), (c + 1, r), (c, r - 1), (c, r + 1)]
    return [s for s in around if s in SQUARES]


def draw_cave(pits=(), agent=None, breezes=()):
    """Draw the cave as text so the class can see what we are doing."""
    print("        +--------+--------+--------+")
    for r in range(ROWS, 0, -1):
        cells = []
        for c in range(1, COLUMNS + 1):
            mark = ""
            if (c, r) in pits:
                mark += "PIT"
            if (c, r) in breezes:
                mark += "~"
            if (c, r) == agent:
                mark += "@"
            cells.append(f"{mark:^8}")
        print(f"   r={r}  |" + "|".join(cells) + "|")
        print("        +--------+--------+--------+")
    print("          c=1      c=2      c=3")
    print("          @ = agent    ~ = breeze felt    PIT = a pit")


# ---------------------------------------------------------------------
# THE RULES THE AGENT IS TOLD BEFORE IT STARTS
# These are true in every cave, whatever the pits turn out to be.
# ---------------------------------------------------------------------
def rules_in_words():
    lines = ["[1,1] has no pit - the agent starts there."]
    for square in [(1, 1), (2, 1)]:
        ns = " or ".join(f"[{c},{r}]" for c, r in neighbours(square))
        lines.append(f"Breeze in [{square[0]},{square[1]}]  "
                     f"if and only if  a pit in {ns}")
    return lines


if __name__ == "__main__":
    print("PART 1: why an agent needs to reason")
    print("=" * 66)

    # ---------- A: the cave, as the agent will never see it ------------
    TRUE_PITS = [(3, 1)]           # the agent is NOT told this
    print("\n[A] The real cave (the agent cannot see this)")
    breezy = sorted({n for p in TRUE_PITS for n in neighbours(p)})
    draw_cave(pits=TRUE_PITS, breezes=breezy)

    # ---------- B: what the agent actually gets -----------------------
    print("\n[B] What the agent gets instead")
    print("   Before it starts, it is told these rules:")
    for i, line in enumerate(rules_in_words(), 1):
        print(f"      R{i}. {line}")
    print("\n   Then it walks, and FEELS one thing per square:")
    print("      at [1,1] : no breeze")
    print("      at [2,1] : BREEZE")
    print("\n   That is all. No map, no pit locations, nothing else.")

    # ---------- C: the reacting agent ---------------------------------
    print("\n[C] A REACTING agent - the kind we wrote in Week 2")
    print("    Its whole brain is a table of if-statements:")
    print("""
      if breeze_here:
          go back the way I came
      else:
          step forward
    """)
    print("   Walk it through:")
    print("      [1,1] no breeze  -> step forward to [2,1]")
    print("      [2,1] BREEZE     -> go back to [1,1]")
    print("      [1,1] no breeze  -> step forward to [2,1]")
    print("      [2,1] BREEZE     -> go back to [1,1]")
    print("\n   It is STUCK in a loop, for ever.")
    print("   It never works out that [1,2] was safe the whole time,")
    print("   because it has no way to COMBINE two percepts.")

    # ---------- D: the reasoning a human does -------------------------
    print("\n[D] What a human does in two seconds")
    print("   1. No breeze at [1,1].")
    print("      R2 says a breeze at [1,1] means a pit at [2,1] or [1,2].")
    print("      No breeze, so NEITHER has a pit.")
    print("      ==> [2,1] is safe AND [1,2] is safe.")
    print("\n   2. Breeze at [2,1].")
    print("      R3 says that means a pit at [1,1], [3,1] or [2,2].")
    print("      [1,1] is safe by R1, so the pit is at [3,1] or [2,2].")
    print("      ==> we do NOT know which one. But we know to avoid both.")

    print("\n   Notice what just happened. From a rule plus a percept we")
    print("   produced a fact about a square the agent has NEVER visited.")
    print("   That is INFERENCE, and no table of if-statements can do it.")

    # ---------- E: the three facts we will prove with code ------------
    print("\n[E] The three questions this week will answer with code")
    print(f"   {'question':<34}{'answer we expect':>20}")
    print(f"   {'-' * 54}")
    for q, a in [("Is [1,2] free of a pit?", "YES - provable"),
                 ("Is [2,2] free of a pit?", "UNKNOWN"),
                 ("Is there a pit in [3,1] or [2,2]?", "YES - provable")]:
        print(f"   {q:<34}{a:>20}")

    print("\n   The middle one matters most. A knowledge-based agent is")
    print("   allowed to answer UNKNOWN. It does not guess, and it does")
    print("   not assume something is false just because it cannot be")
    print("   proved true.")

    # ---------- F: the vocabulary -------------------------------------
    print("\n[F] The three words for the rest of the week")
    print("   KNOWLEDGE BASE  the list of sentences the agent believes")
    print("   TELL            add a sentence to that list")
    print("   ASK             ask whether a sentence FOLLOWS from it")
    print("\n   TELL is easy - it is list.append().")
    print("   ASK is the hard part, and it is the whole of Parts 3 to 8.")
    print("\n   Part 2 starts by writing those sentences down in a form")
    print("   Python can actually work with.")
