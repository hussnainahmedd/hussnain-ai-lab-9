# =====================================================================
# CS344L - AI Lab | Week 9 | PART 8 of 8
# Topic : WHICH METHOD, AND WHERE BOTH OF THEM STOP
# Teacher: Raja Faisal Umar
# Run    : python part8_compare.py
# =====================================================================
# Two methods now answer the same question:
#
#   MODEL CHECKING (Part 5)  build all 2^n caves, keep the ones that
#                            fit, look at the answer column
#   RESOLUTION     (Part 7)  assume the opposite and hunt for the
#                            empty clause
#
# Both are SOUND (they never tell you something false) and COMPLETE
# (if it follows, they will find it). So the choice is about cost.
#
# To measure that we need caves of different sizes. We use a CORRIDOR:
# n squares in a row, each one next to the ones beside it. The agent
# stands in square 1 and feels no breeze, which proves square 2 is
# safe. Only the SIZE of the cave changes, so the comparison is fair.
#
# This file runs for about 10 seconds. Both methods are given work
# that is genuinely hard for them, and each one loses once.
# =====================================================================

import time

from part2_syntax import NOT, OR, AND, IFF, show, symbols_in
from part3_semantics import evaluate
from part4_truth_tables import all_models
from part5_entailment import entails
from part6_cnf import knowledge_base_clauses
from part7_resolution import resolution
from part2_syntax import cave_knowledge_base


def corridor_knowledge_base(n):
    """A cave of n squares in a row, with the agent in square 1.

    Square i is next to square i-1 and square i+1, and nothing else.
    The agent is told every breeze rule, and feels no breeze where
    it stands.
    """
    knowledge_base = [NOT("P1")]                  # square 1 is safe

    for i in range(1, n + 1):
        neighbours = [f"P{j}" for j in (i - 1, i + 1) if 1 <= j <= n]
        combined = neighbours[0]
        for extra in neighbours[1:]:
            combined = OR(combined, extra)
        knowledge_base.append(IFF(f"B{i}", combined))

    knowledge_base.append(NOT("B1"))              # percept: no breeze here
    return knowledge_base


def count_symbols(knowledge_base, query):
    names = set()
    for sentence in list(knowledge_base) + [query]:
        symbols_in(sentence, names)
    return len(names)


if __name__ == "__main__":
    print("PART 8: which method, and where both of them stop")
    print("=" * 70)
    overall = time.time()

    # ---------- A: the two methods side by side ------------------------
    print("\n[A] The same job, two completely different plans")
    print(f"\n   {'':<22}{'model checking':<24}{'resolution'}")
    rows = [
        ("works on", "any sentence", "clauses only (CNF)"),
        ("builds", "every possible cave", "new clauses"),
        ("cost grows with", "2 ^ symbols", "clauses it can derive"),
        ("stops when", "all models checked", "it finds {} or runs dry"),
        ("gives you", "a yes or no", "a yes or no, plus a proof"),
        ("easy to write?", "yes, 10 lines", "harder, about 40"),
    ]
    for label, left, right in rows:
        print(f"   {label:<22}{left:<24}{right}")

    # ---------- B: the corridor ----------------------------------------
    print("\n[B] The test cave: a corridor of n squares")
    print("\n      +----+----+----+----+----+")
    print("      | @  |    |    |    |    |     @ = agent, no breeze")
    print("      +----+----+----+----+----+")
    print("        1    2    3    4    5")
    print("\n   Square 1's only neighbour is square 2, and the agent")
    print("   feels no breeze. So square 2 must be safe, for any n.")
    print("   We ask both methods to prove it, for growing n.")

    example = corridor_knowledge_base(4)
    print(f"\n   For n = 4 the knowledge base is:")
    for sentence in example:
        print(f"      {show(sentence)}")

    # ---------- C: the measurement -------------------------------------
    print("\n[C] Proving square 2 is safe, as the cave grows")
    query = NOT("P2")
    print(f"\n   {'n':>3}{'symbols':>9}{'models':>12}{'tables (s)':>13}"
          f"{'steps':>8}{'resolution (s)':>16}")

    for n in (3, 4, 5, 6, 7, 8, 9):
        knowledge_base = corridor_knowledge_base(n)
        count = count_symbols(knowledge_base, query)

        start = time.time()
        by_table = entails(knowledge_base, query)
        table_time = time.time() - start

        start = time.time()
        by_resolution, steps, _ = resolution(knowledge_base, query)
        resolution_time = time.time() - start

        assert by_table == by_resolution == True
        print(f"   {n:>3}{count:>9}{2 ** count:>12,}{table_time:>13.3f}"
              f"{steps:>8}{resolution_time:>16.3f}")

    print("\n   The models column DOUBLES with every square added, and")
    print("   the truth-table time follows it. Resolution barely moves:")
    print("   it finds the same two-step proof however big the cave is,")
    print("   because the proof never depended on the far squares.")

    # ---------- D: the case that is bad for resolution -----------------
    print("\n[D] But resolution is not always the winner")
    print("\n   Ask instead whether square 3 is safe. It is NOT, and")
    print("   the agent cannot prove either way - the answer is UNKNOWN.")
    print("   Now resolution cannot stop early: to say 'no proof' it")
    print("   must first derive every clause it possibly can.")
    query_unknown = NOT("P3")
    print(f"\n   {'n':>3}{'symbols':>9}{'tables (s)':>13}{'steps':>12}"
          f"{'clauses':>10}{'resolution (s)':>16}")
    for n in (3, 4, 5, 6, 7, 8):
        knowledge_base = corridor_knowledge_base(n)
        count = count_symbols(knowledge_base, query_unknown)

        start = time.time()
        by_table = entails(knowledge_base, query_unknown)
        table_time = time.time() - start

        start = time.time()
        by_resolution, steps, held = resolution(
            knowledge_base, query_unknown, limit=50_000_000)
        resolution_time = time.time() - start

        assert by_table is False and by_resolution is False
        print(f"   {n:>3}{count:>9}{table_time:>13.3f}{steps:>12,}"
              f"{held:>10,}{resolution_time:>16.3f}")

    print("\n   The tables are unbothered - they always do exactly 2^n")
    print("   rows whatever the question. Resolution goes from 118")
    print("   steps to over a million, and ends up SLOWER than the")
    print("   method it beat so easily two tables ago.")
    print("\n   So the real rule is: resolution wins when there IS a")
    print("   short proof, and loses when it has to prove there is no")
    print("   proof at all. No method is best at everything - the same")
    print("   lesson as the No Free Lunch result in Week 8.")

    # ---------- E: back to the real cave -------------------------------
    print("\n[E] Back to our 3x2 cave")
    knowledge_base = cave_knowledge_base()
    clauses = knowledge_base_clauses(knowledge_base)
    print(f"   knowledge base : {len(knowledge_base)} sentences, "
          f"{len(clauses)} clauses")

    questions = [
        ("no pit at [1,2]?", NOT("P12")),
        ("no pit at [2,1]?", NOT("P21")),
        ("no pit at [2,2]?", NOT("P22")),
        ("pit in [3,1] or [2,2]?", OR("P31", "P22")),
    ]
    print(f"\n   {'question':<26}{'answer':>9}{'models built':>15}"
          f"{'resolution steps':>19}")
    for label, q in questions:
        answer, checked, _, _ = entails(knowledge_base, q, report=True)
        _, steps, _ = resolution(knowledge_base, q)
        print(f"   {label:<26}{str(answer):>9}{checked:>15}{steps:>19}")

    print("\n   Read the last two columns honestly. Model checking")
    print("   always does exactly 128 models. Resolution does 43 steps")
    print("   for the easy proofs - far less - but 245 for the last")
    print("   one, which is MORE than model checking.")
    print("\n   On a cave this small it does not matter. The reason to")
    print("   learn resolution is the table in [C], where the cave is")
    print("   big enough that 2^n stops being an option at all.")

    # ---------- F: what propositional logic cannot say -----------------
    print("\n[F] The real limit, and it is not speed")
    print("   Our cave needed a separate rule for every single square:")
    print("      B11 <=> (P21 | P12)")
    print("      B21 <=> (P11 | P31 | P22)")
    print("      ... one for each square, written out by hand")
    print("\n   What we WANT to say is one sentence:")
    print("      'for every square x, a breeze at x means a pit next")
    print("       to x'")
    print("\n   Propositional logic cannot say 'for every'. It has no")
    print("   variables, so a 4x4 cave needs 16 breeze rules and a")
    print("   100x100 cave needs 10,000 of them - all saying the same")
    print("   thing about different squares.")
    print("\n   Adding 'for every' and 'there exists' gives you FIRST")
    print("   ORDER LOGIC, which is Knowledge-Based Agents II.")

    # ---------- G: the week in eight lines -----------------------------
    print("\n[G] WEEK 9 IN EIGHT LINES")
    print("   1. A knowledge-based agent stores sentences and reasons")
    print("      from them; a reacting agent cannot combine percepts.")
    print("   2. A sentence is syntax - a shape. It means nothing until")
    print("      a model gives every symbol a value.")
    print("   3. A model is one possible world. n symbols, 2^n worlds.")
    print("   4. KB |= A means A is true in EVERY model where KB is.")
    print("   5. Not entailed means UNKNOWN, never false. This is the")
    print("      mistake that kills the agent.")
    print("   6. Truth tables always work and are hopeless past about")
    print("      25 symbols.")
    print("   7. Resolution proves by contradiction on CNF clauses, and")
    print("      gives the same answers with far less work - usually.")
    print("   8. Neither can say 'for every square'. That needs first")
    print("      order logic.")

    print(f"\n   (total time {time.time() - overall:.1f} seconds)")
