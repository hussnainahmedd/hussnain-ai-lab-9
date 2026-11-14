# =====================================================================
# CS344L - AI Lab | Week 9 | PART 6 of 8
# Topic : CNF - rewriting every sentence into one standard shape
# Teacher: Raja Faisal Umar
# Run    : python part6_cnf.py
# =====================================================================
# Resolution, in Part 7, is a very fast proof method - but it is fussy.
# It only works on sentences in CONJUNCTIVE NORMAL FORM:
#
#     an AND of ORs      (P21 | P12) & (~B11 | P21 | P12) & (~P11)
#
# Each bracket is a CLAUSE: an OR of plain symbols and negated symbols.
# The whole sentence is those clauses ANDed together.
#
# Every sentence in propositional logic can be rewritten into CNF
# without changing its meaning. We do it in four steps, and every step
# is one of the laws we already proved with a truth table in Part 4:
#
#     1. get rid of <=>     using  A<=>B  ==  (A=>B) & (B=>A)
#     2. get rid of =>      using  A=>B   ==  ~A | B
#     3. push ~ inwards     using  De Morgan and ~~A == A
#     4. pull & outwards    using  A|(B&C) == (A|B) & (A|C)
#
# After step 4 the only ~ signs left sit directly on symbols, and the
# sentence is an AND of ORs. We then store each clause as a SET of
# literals, which makes Part 7 almost trivial to write.
# =====================================================================

from part2_syntax import (NOT, AND, OR, IMPLIES, IFF, show, is_symbol,
                          cave_knowledge_base)
from part4_truth_tables import equivalent


# ---------------------------------------------------------------------
# STEP 1: A <=> B  becomes  (A => B) & (B => A)
# ---------------------------------------------------------------------
def eliminate_iff(s):
    if is_symbol(s):
        return s
    parts = [eliminate_iff(p) for p in s[1:]]
    if s[0] == "<=>":
        a, b = parts
        return AND(IMPLIES(a, b), IMPLIES(b, a))
    return (s[0],) + tuple(parts)


# ---------------------------------------------------------------------
# STEP 2: A => B  becomes  ~A | B
# ---------------------------------------------------------------------
def eliminate_implies(s):
    if is_symbol(s):
        return s
    parts = [eliminate_implies(p) for p in s[1:]]
    if s[0] == "=>":
        a, b = parts
        return OR(NOT(a), b)
    return (s[0],) + tuple(parts)


# ---------------------------------------------------------------------
# STEP 3: push every ~ down until it sits on a symbol
# ---------------------------------------------------------------------
def move_not_inwards(s):
    if is_symbol(s):
        return s

    if s[0] == "not":
        inside = s[1]
        if is_symbol(inside):
            return s                              # already as deep as it goes
        if inside[0] == "not":
            return move_not_inwards(inside[1])    # ~~A becomes A
        if inside[0] == "and":                    # De Morgan
            a, b = inside[1], inside[2]
            return OR(move_not_inwards(NOT(a)), move_not_inwards(NOT(b)))
        if inside[0] == "or":                     # De Morgan
            a, b = inside[1], inside[2]
            return AND(move_not_inwards(NOT(a)), move_not_inwards(NOT(b)))

    return (s[0],) + tuple(move_not_inwards(p) for p in s[1:])


# ---------------------------------------------------------------------
# STEP 4: pull the ANDs outside the ORs
# ---------------------------------------------------------------------
def distribute(s):
    if is_symbol(s) or s[0] == "not":
        return s

    a, b = distribute(s[1]), distribute(s[2])

    if s[0] == "or":
        # A | (B & C)  becomes  (A|B) & (A|C)
        if not is_symbol(b) and b[0] == "and":
            return AND(distribute(OR(a, b[1])), distribute(OR(a, b[2])))
        # (B & C) | A  becomes  (B|A) & (C|A)
        if not is_symbol(a) and a[0] == "and":
            return AND(distribute(OR(a[1], b)), distribute(OR(a[2], b)))

    return (s[0], a, b)


def to_cnf(sentence):
    """Run all four steps in order."""
    s = eliminate_iff(sentence)
    s = eliminate_implies(s)
    s = move_not_inwards(s)
    return distribute(s)


def to_cnf_steps(sentence):
    """Same thing, but keep every intermediate result for the slides."""
    one = eliminate_iff(sentence)
    two = eliminate_implies(one)
    three = move_not_inwards(two)
    four = distribute(three)
    return [("start", sentence), ("1. no <=>", one), ("2. no =>", two),
            ("3. ~ on symbols only", three), ("4. and outside", four)]


# ---------------------------------------------------------------------
# TURNING THE CNF TREE INTO A LIST OF CLAUSES
# A literal is a string: "P21" or "~P21".
# A clause is a frozenset of literals, so {"~B11", "P21", "P12"}.
# ---------------------------------------------------------------------
def literal_of(s):
    return "~" + s[1] if s[0] == "not" else s


def split_on(s, operator):
    """Flatten a chain like ((a & b) & c) into [a, b, c]."""
    if is_symbol(s) or s[0] != operator:
        return [s]
    return split_on(s[1], operator) + split_on(s[2], operator)


def clauses_of(sentence):
    """Convert to CNF, then return it as a list of clauses (sets)."""
    cnf = to_cnf(sentence)
    result = []
    for part in split_on(cnf, "and"):
        literals = frozenset(literal_of(p) for p in split_on(part, "or"))
        result.append(literals)
    return result


def clause_text(clause):
    """Print a clause the way we would write it on the board."""
    if not clause:
        return "{}  <- the empty clause"
    return "{" + ", ".join(sorted(clause)) + "}"


def knowledge_base_clauses(knowledge_base):
    """Every clause from every sentence, with duplicates removed."""
    seen, result = set(), []
    for sentence in knowledge_base:
        for clause in clauses_of(sentence):
            if clause not in seen:
                seen.add(clause)
                result.append(clause)
    return result


if __name__ == "__main__":
    print("PART 6: conjunctive normal form")
    print("=" * 66)

    # ---------- A: one rule, step by step -----------------------------
    print("\n[A] One cave rule, converted one step at a time")
    rule = IFF("B11", OR("P21", "P12"))
    for label, form in to_cnf_steps(rule):
        print(f"\n   {label}")
        print(f"      {show(form)}")

    print("\n   Four steps, and the meaning never changed. We can check")
    print("   that claim rather than trust it:")
    print(f"      original equivalent to final CNF? "
          f"{equivalent(rule, to_cnf(rule))}")

    # ---------- B: as clauses -----------------------------------------
    print("\n[B] The same CNF, stored as clauses")
    for clause in clauses_of(rule):
        print(f"      {clause_text(clause)}")
    print("\n   A clause is a SET, so the order inside it does not")
    print("   matter and repeats disappear by themselves. That is")
    print("   exactly what Part 7 needs.")

    # ---------- C: reading a clause as a rule -------------------------
    print("\n[C] How to read a clause out loud")
    print("   {~B11, P21, P12}")
    print("      means  ~B11 | P21 | P12")
    print("      which is  B11 => (P21 | P12)")
    print("      read as  'if there is a breeze at [1,1], then there")
    print("                is a pit at [2,1] or at [1,2]'")
    print("\n   Every clause is a rule in disguise. A clause with one")
    print("   negative literal and one positive is just an arrow.")

    # ---------- D: more conversions -----------------------------------
    print("\n[D] A few more, to show the machine handles anything")
    samples = [
        NOT("P11"),
        "B21",
        IMPLIES("P21", "B11"),
        NOT(AND("A", "B")),
        NOT(OR("A", AND("B", "C"))),
        IFF("A", AND("B", "C")),
    ]
    print(f"\n   {'sentence':<24}{'clauses'}")
    for sentence in samples:
        pieces = "  ".join(clause_text(c) for c in clauses_of(sentence))
        print(f"   {show(sentence):<24}{pieces}")

    # ---------- E: the whole knowledge base ---------------------------
    print("\n[E] The agent's whole knowledge base, as clauses")
    knowledge_base = cave_knowledge_base()
    clauses = knowledge_base_clauses(knowledge_base)
    for sentence in knowledge_base:
        print(f"\n   {show(sentence)}")
        for clause in clauses_of(sentence):
            print(f"      {clause_text(clause)}")
    print(f"\n   {len(knowledge_base)} sentences became "
          f"{len(clauses)} different clauses.")

    # ---------- F: the honest warning ---------------------------------
    print("\n[F] The price of step 4")
    print("   Distributing OR over AND can make a sentence explode.")
    print("   The worst shape is (A1 & B1) | (A2 & B2) | (A3 & B3) | ...")
    print(f"\n   {'brackets ORed together':<26}{'symbols':>9}{'clauses':>10}")
    for n in (2, 3, 4, 5, 6):
        # (A1 & B1) | (A2 & B2) | ... - the worst case for distribution
        s = AND("A1", "B1")
        for i in range(2, n + 1):
            s = OR(s, AND(f"A{i}", f"B{i}"))
        print(f"   {n:<26}{2 * n:>9}{len(clauses_of(s)):>10}")

    print("\n   Each extra bracket DOUBLES the clause count. In the")
    print("   worst case CNF conversion is exponential too.")
    print("\n   In practice it is almost never that bad: real rules look")
    print("   like our cave rules and convert to a handful of clauses.")
    print("   But it is honest to know the worst case is there.")
    print("\n   Now that everything is clauses, Part 7 can prove things")
    print("   without ever building a model.")
