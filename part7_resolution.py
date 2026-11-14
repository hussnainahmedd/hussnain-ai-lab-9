# =====================================================================
# CS344L - AI Lab | Week 9 | PART 7 of 8
# Topic : RESOLUTION - proving things without building models
# Teacher: Raja Faisal Umar
# Run    : python part7_resolution.py
# =====================================================================
# Part 5 answered every question by building 128 caves. Resolution
# answers the same questions without building a single one.
#
# THE ONE RULE. Take two clauses where some symbol appears plain in
# one and negated in the other. Delete that pair and glue the rest
# together:
#
#       {A, B}   and   {~A, C}       ->      {B, C}
#
# Why is that allowed? Either A is true or it is false. If A is true,
# the second clause still needs C. If A is false, the first still
# needs B. Either way, B or C must hold. So {B, C} follows.
#
# PROOF BY CONTRADICTION. To prove KB |= alpha we do NOT try to derive
# alpha. We add the OPPOSITE of alpha to the knowledge base and try to
# derive nonsense:
#
#       KB together with ~alpha  ->  a contradiction
#       means alpha had to be true all along
#
# The contradiction shows up as the EMPTY CLAUSE {}. An empty clause
# is a clause with nothing left to satisfy it, so it can never be
# true - and reaching it means the assumption was impossible.
# =====================================================================

from part2_syntax import (NOT, AND, OR, show, is_symbol,
                          cave_knowledge_base)
from part6_cnf import clauses_of, clause_text, knowledge_base_clauses


def negate_literal(literal):
    """P21 becomes ~P21, and ~P21 becomes P21."""
    return literal[1:] if literal.startswith("~") else "~" + literal


def resolve(clause_a, clause_b):
    """Every clause that can be produced from this pair in one step."""
    results = []
    for literal in clause_a:
        if negate_literal(literal) in clause_b:
            merged = (clause_a - {literal}) | (clause_b - {negate_literal(literal)})
            results.append((literal, frozenset(merged)))
    return results


def is_tautology(clause):
    """A clause holding both A and ~A is always true - useless to keep."""
    return any(negate_literal(l) in clause for l in clause)


def simplify_not(sentence):
    """~~X is just X - only used to print the assumption readably."""
    if not is_symbol(sentence) and sentence[0] == "not":
        inside = sentence[1]
        if not is_symbol(inside) and inside[0] == "not":
            return simplify_not(inside[1])
    return sentence


def extract_proof(empty_from, parents):
    """Walk back from the empty clause and keep only the steps used."""
    needed, order = set(), []

    def visit(clause):
        if clause in needed:
            return
        needed.add(clause)
        if clause in parents:
            left, right, literal = parents[clause]
            visit(left)
            visit(right)
            order.append((left, right, literal, clause))

    visit(empty_from)
    return order


def resolution(knowledge_base, query, trace=False, limit=4000, proof=False):
    """Does the knowledge base entail the query? Proof by contradiction."""
    # The clauses of the knowledge base, plus the clauses of NOT query.
    clauses = list(knowledge_base_clauses(knowledge_base))
    goal_clauses = clauses_of(NOT(query))

    if trace:
        print("   starting clauses, from the knowledge base:")
        for c in clauses:
            print(f"      {clause_text(c)}")
        print(f"\n   now ASSUME THE OPPOSITE: "
              f"{show(simplify_not(NOT(query)))}")
        for c in goal_clauses:
            print(f"      {clause_text(c)}   <- the assumption")

    clauses = clauses + [c for c in goal_clauses if c not in clauses]
    known = set(clauses)
    parents = {}            # resolvent -> (parent, parent, cancelled literal)
    steps = 0

    if trace:
        print("\n   resolving:")

    while True:
        new_clauses = []
        # Try every pair of clauses we currently hold.
        for i in range(len(clauses)):
            for j in range(i + 1, len(clauses)):
                for literal, resolvent in resolve(clauses[i], clauses[j]):
                    steps += 1
                    if is_tautology(resolvent):
                        continue

                    if not resolvent:                 # the empty clause
                        parents[resolvent] = (clauses[i], clauses[j],
                                              literal)
                        if proof:
                            return (True, steps, len(clauses),
                                    extract_proof(resolvent, parents))
                        return True, steps, len(clauses)

                    if resolvent not in known:
                        known.add(resolvent)
                        parents[resolvent] = (clauses[i], clauses[j],
                                              literal)
                        new_clauses.append(resolvent)
                        if trace:
                            print(f"      {clause_text(clauses[i])}  +  "
                                  f"{clause_text(clauses[j])}")
                            print(f"         cancel {literal} -> "
                                  f"{clause_text(resolvent)}")
                    if steps > limit:
                        return None, steps, len(clauses)

        # Nothing new was produced, so no contradiction can ever appear.
        if not new_clauses:
            if trace:
                print("      no new clause can be made - we stop")
            if proof:
                return False, steps, len(clauses), []
            return False, steps, len(clauses)

        clauses = clauses + new_clauses


if __name__ == "__main__":
    print("PART 7: resolution")
    print("=" * 66)

    knowledge_base = cave_knowledge_base()

    # ---------- A: the rule on its own --------------------------------
    print("\n[A] The resolution rule, on two clauses")
    a = frozenset({"P21", "P12"})
    b = frozenset({"~P21", "B11"})
    print(f"      {clause_text(a)}")
    print(f"      {clause_text(b)}")
    for literal, resolvent in resolve(a, b):
        print(f"      cancel {literal} and {negate_literal(literal)}"
              f"  ->  {clause_text(resolvent)}")
    print("\n   P21 cannot be true and false at the same time, so")
    print("   whichever way it goes, P12 or B11 has to hold.")

    # ---------- B: a full proof, printed -------------------------------
    print("\n[B] Proving [1,2] is safe:  KB |= ~P12")
    print("\n   Step 1 - the knowledge base as clauses:")
    for c in knowledge_base_clauses(knowledge_base):
        print(f"      {clause_text(c)}")
    print("\n   Step 2 - assume the OPPOSITE of what we want to prove.")
    print("      we want  ~P12   so we assume  P12")
    for c in clauses_of(NOT(NOT("P12"))):
        print(f"      {clause_text(c)}   <- the assumption")

    answer, steps, held, chain = resolution(
        knowledge_base, NOT("P12"), proof=True)

    print("\n   Step 3 - resolve until something breaks.")
    print("   Out of all the work it did, these are the steps that")
    print("   actually mattered:")
    for left, right, literal, result in chain:
        shown = clause_text(result) if result else "{}   CONTRADICTION"
        print(f"\n      {clause_text(left)}")
        print(f"      {clause_text(right)}")
        print(f"      cancel {literal:<6} ->  {shown}")

    print(f"\n   proved? {answer}")
    print(f"   resolution steps tried : {steps}")
    print(f"   steps actually needed  : {len(chain)}")
    print("\n   We assumed there WAS a pit at [1,2] and the assumption")
    print("   collided with the rules. So there is no pit at [1,2] -")
    print("   the same answer Part 5 got by building 128 caves.")

    # ---------- C: when there is no proof ------------------------------
    print("\n[C] Now ask something the agent does NOT know:  KB |= ~P22")
    answer, steps, held = resolution(knowledge_base, NOT("P22"))
    print(f"   proved? {answer}   (steps tried: {steps}, "
          f"clauses held at the end: {held})")
    print("\n   Resolution ran out of new clauses without ever reaching")
    print("   the empty clause. No contradiction means no proof, and")
    print("   no proof means UNKNOWN - the same answer as Part 5.")

    # ---------- D: every question, both methods ------------------------
    print("\n[D] Resolution against model checking, same six questions")
    from part5_entailment import entails

    questions = [
        ("no pit at [1,2]?", NOT("P12")),
        ("no pit at [2,1]?", NOT("P21")),
        ("no pit at [2,2]?", NOT("P22")),
        ("IS there a pit at [2,2]?", "P22"),
        ("pit in [3,1] or [2,2]?", OR("P31", "P22")),
        ("pit in BOTH?", AND("P31", "P22")),
    ]
    print(f"\n   {'question':<30}{'truth tables':>14}{'resolution':>13}"
          f"{'agree?':>9}")
    for label, query in questions:
        by_table = entails(knowledge_base, query)
        by_resolution, _, _ = resolution(knowledge_base, query)
        print(f"   {label:<30}{str(by_table):>14}{str(by_resolution):>13}"
              f"{str(by_table == by_resolution):>9}")

    print("\n   Every answer matches. That is the point: resolution is")
    print("   not a shortcut that trades accuracy for speed. It gives")
    print("   the SAME answers, by a completely different route.")

    # ---------- E: why the empty clause means contradiction ------------
    print("\n[E] Why {} means 'impossible'")
    print("   A clause is a list of ways to be satisfied:")
    print("      {P21, P12}   has two ways - P21, or P12")
    print("      {P21}        has one way")
    print("      {}           has NO way at all")
    print("\n   So a knowledge base that produces {} is claiming")
    print("   something with no way of being true. Since the original")
    print("   rules were fine, the fault must be the one thing we")
    print("   added: the assumption. So the assumption was wrong, and")
    print("   its opposite - what we wanted to prove - is right.")

    # ---------- F: the honest limits -----------------------------------
    print("\n[F] What resolution does NOT give you")
    print("   1. It proves, it does not explore. Resolution can tell")
    print("      you [1,2] is safe. It cannot tell you where the pit")
    print("      is when the knowledge base does not pin it down.")
    print("\n   2. 'Not proved' is not 'false'. Exactly as in Part 5,")
    print("      the honest answer there is UNKNOWN.")
    print("\n   3. It is complete but not fast in the worst case. The")
    print("      clause set can still grow exponentially - Part 8")
    print("      measures how our cave actually behaves.")
    print("\n   4. It cannot say 'every square next to a pit'. For that")
    print("      you need variables and quantifiers, which is first")
    print("      order logic - Knowledge-Based Agents II.")
