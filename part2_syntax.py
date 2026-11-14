# =====================================================================
# CS344L - AI Lab | Week 9 | PART 2 of 8
# Topic : SYNTAX - writing a sentence down so Python can hold it
# Teacher: Raja Faisal Umar
# Run    : python part2_syntax.py
# =====================================================================
# A sentence like
#
#     Breeze in [1,1]  if and only if  a pit in [2,1] or [1,2]
#
# is English. Python cannot do anything with English. We need a shape
# that a program can take apart.
#
# We use NESTED TUPLES. Every sentence is one of five shapes:
#
#     "P21"                     a SYMBOL - a plain string
#     ("not", x)                NOT x
#     ("and", x, y)             x AND y
#     ("or",  x, y)             x OR  y
#     ("=>",  x, y)             x IMPLIES y      (if x then y)
#     ("<=>", x, y)             x IF AND ONLY IF y
#
# That is the whole language. Everything else this week is built out
# of these six lines.
#
# Note there is no "maybe" and no "probably". A symbol is either true
# or false, nothing in between. That is why it is called PROPOSITIONAL
# logic, and it is both the strength and the limit of this method.
# =====================================================================

from part1_knowledge_base import SQUARES, name, neighbours


# ---------------------------------------------------------------------
# Little helpers so we can build sentences that READ like sentences.
# These are just shortcuts for making tuples - nothing clever.
# ---------------------------------------------------------------------
def NOT(x):
    return ("not", x)


def AND(x, y):
    return ("and", x, y)


def OR(x, y):
    return ("or", x, y)


def IMPLIES(x, y):
    return ("=>", x, y)


def IFF(x, y):
    return ("<=>", x, y)


def is_symbol(sentence):
    """A symbol is just a string, like 'P21'. Everything else is a tuple."""
    return isinstance(sentence, str)


# ---------------------------------------------------------------------
# PRETTY PRINTING
# The tuples are easy for Python and horrible for humans, so we write
# a function that turns them back into something readable.
# ---------------------------------------------------------------------
SIGNS = {"not": "~", "and": " & ", "or": " | ", "=>": " => ", "<=>": " <=> "}


def show(sentence):
    """Turn a sentence tuple back into readable text."""
    if is_symbol(sentence):
        return sentence
    operator = sentence[0]
    if operator == "not":
        return "~" + show(sentence[1])
    left, right = sentence[1], sentence[2]
    return "(" + show(left) + SIGNS[operator] + show(right) + ")"


def symbols_in(sentence, found=None):
    """Collect every symbol name used anywhere inside a sentence."""
    if found is None:
        found = set()
    if is_symbol(sentence):
        found.add(sentence)
    else:
        for part in sentence[1:]:
            symbols_in(part, found)
    return found


def depth(sentence):
    """How deeply nested the sentence is - 0 for a bare symbol."""
    if is_symbol(sentence):
        return 0
    return 1 + max(depth(part) for part in sentence[1:])


# ---------------------------------------------------------------------
# BUILDING THE CAVE'S KNOWLEDGE BASE
# Instead of typing every rule by hand, we build them from the cave.
# This is the normal way: a few lines of code generate many sentences.
# ---------------------------------------------------------------------
def breeze_rule(square):
    """Breeze here  <=>  a pit in one of my neighbours."""
    pits = [name("P", n) for n in neighbours(square)]
    combined = pits[0]
    for extra in pits[1:]:            # OR them all together, one at a time
        combined = OR(combined, extra)
    return IFF(name("B", square), combined)


def cave_knowledge_base():
    """The five sentences the agent believes after two steps."""
    return [
        NOT("P11"),                   # R1: the start square is safe
        breeze_rule((1, 1)),          # R2: what a breeze at [1,1] means
        breeze_rule((2, 1)),          # R3: what a breeze at [2,1] means
        NOT("B11"),                   # R4: percept - no breeze at [1,1]
        "B21",                        # R5: percept - BREEZE at [2,1]
    ]


if __name__ == "__main__":
    print("PART 2: syntax - sentences Python can hold")
    print("=" * 66)

    # ---------- A: the five shapes ------------------------------------
    print("\n[A] The five shapes, and nothing else")
    examples = [
        ("a symbol", "P21"),
        ("not", NOT("P21")),
        ("and", AND("P21", "P12")),
        ("or", OR("P21", "P12")),
        ("implies", IMPLIES("B11", "P21")),
        ("if and only if", IFF("B11", "P21")),
    ]
    print(f"\n   {'meaning':<17}{'what Python holds':<34}{'how we read it'}")
    for label, sentence in examples:
        print(f"   {label:<17}{str(sentence):<34}{show(sentence)}")

    # ---------- B: nesting --------------------------------------------
    print("\n[B] Sentences nest inside sentences")
    nested = IFF("B11", OR("P21", "P12"))
    print(f"\n   Python holds : {nested}")
    print(f"   We read it as: {show(nested)}")
    print(f"   symbols used : {sorted(symbols_in(nested))}")
    print(f"   nesting depth: {depth(nested)}")
    print("\n   Read the tuple from the outside in: the outermost")
    print("   operator is '<=>', its left side is the symbol B11, and")
    print("   its right side is another tuple - an 'or'.")

    # ---------- C: the rules, generated by code -----------------------
    print("\n[C] Building the breeze rules from the cave itself")
    for square in [(1, 1), (2, 1)]:
        ns = [f"[{c},{r}]" for c, r in neighbours(square)]
        print(f"\n   [{square[0]},{square[1]}] has neighbours "
              f"{', '.join(ns)}")
        print(f"   rule: {show(breeze_rule(square))}")

    print("\n   We wrote one function and it produced both rules. In a")
    print("   4x4 cave the same function produces all sixteen.")

    # ---------- D: the whole knowledge base ---------------------------
    print("\n[D] The agent's knowledge base after two steps")
    knowledge_base = cave_knowledge_base()
    labels = ["R1 given : the start square is safe",
              "R2 given : what a breeze at [1,1] means",
              "R3 given : what a breeze at [2,1] means",
              "R4 felt  : no breeze at [1,1]",
              "R5 felt  : BREEZE at [2,1]"]
    for label, sentence in zip(labels, knowledge_base):
        print(f"   {label}")
        print(f"            {show(sentence)}")

    every_symbol = set()
    for sentence in knowledge_base:
        symbols_in(sentence, every_symbol)
    print(f"\n   symbols mentioned: {len(every_symbol)}")
    print(f"   {sorted(every_symbol)}")

    # ---------- E: what we have, and what we do not -------------------
    print("\n[E] What we have built so far")
    print("   We can WRITE sentences down. We cannot yet work out")
    print("   whether any of them is true, because a tuple has no")
    print("   meaning on its own - ('and', 'P21', 'P12') is just three")
    print("   strings in a box.")
    print("\n   Giving those tuples MEANING is called semantics, and")
    print("   that is Part 3.")

    # ---------- F: the one thing students get wrong -------------------
    print("\n[F] The trap: '=>' is not 'because'")
    print(f"   {show(IMPLIES('P21', 'B11'))} says only this:")
    print("      IF there is a pit at [2,1], THEN there is a breeze")
    print("      at [1,1].")
    print("\n   It does NOT say the pit caused the breeze, and it does")
    print("   NOT work backwards. From a breeze you may not conclude a")
    print("   pit at [2,1] - the breeze could come from another square.")
    print("\n   That is exactly why the cave rules use '<=>' and not")
    print("   '=>'. We need it to work in BOTH directions.")
