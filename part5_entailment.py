# =====================================================================
# CS344L - AI Lab | Week 9 | PART 5 of 8
# Topic : ENTAILMENT - what the agent actually KNOWS
# Teacher: Raja Faisal Umar
# Run    : python part5_entailment.py
# =====================================================================
# ENTAILMENT is the idea the whole week is built on:
#
#     KB entails A   means   in EVERY model where the whole knowledge
#                            base is true, A is true as well.
#
# Written  KB |= A  and read "KB entails A".
#
# The method is brutally simple. Go through all 2^n models. Throw away
# every one that breaks the knowledge base. Look at what is left: if A
# is true in all of them, the agent knows A. If A is false in even one
# of them, the agent does NOT know A - it is only a guess.
#
# This algorithm is called TT-ENTAILS in the textbook. It is correct,
# it is easy to write, and it is far too slow for a real problem -
# which is why Parts 6 and 7 exist.
#
# One warning before we start. "KB does not entail A" does NOT mean A
# is false. It means UNKNOWN. Mixing those two up is the single most
# common mistake in this whole topic.
# =====================================================================

from part1_knowledge_base import draw_cave
from part2_syntax import (NOT, AND, OR, show, symbols_in,
                          cave_knowledge_base)
from part3_semantics import evaluate
from part4_truth_tables import all_models


def entails(knowledge_base, query, report=False):
    """Does the knowledge base entail the query? Checks every model."""
    names = set()
    for sentence in list(knowledge_base) + [query]:
        symbols_in(sentence, names)
    names = sorted(names)

    checked = surviving = 0
    counterexample = None

    for model in all_models(names):
        checked += 1
        # Is every sentence in the knowledge base true in this model?
        if not all(evaluate(s, model) for s in knowledge_base):
            continue                    # impossible cave - throw it away
        surviving += 1
        if not evaluate(query, model):
            # A cave that fits everything we know, yet the query fails.
            # One of these is enough to prove the agent does NOT know it.
            if counterexample is None:
                counterexample = model

    answer = counterexample is None
    if report:
        return answer, checked, surviving, counterexample
    return answer


def pit_symbols(names):
    return [n for n in names if n.startswith("P")]


if __name__ == "__main__":
    print("PART 5: entailment - what the agent knows")
    print("=" * 66)

    knowledge_base = cave_knowledge_base()
    names = set()
    for sentence in knowledge_base:
        symbols_in(sentence, names)
    names = sorted(names)

    # ---------- A: the situation --------------------------------------
    print("\n[A] Where the agent is standing")
    draw_cave(agent=(2, 1), breezes=[(2, 1)])
    print("\n   It felt no breeze at [1,1], then a breeze at [2,1].")
    print(f"   Its knowledge base has {len(knowledge_base)} sentences and "
          f"mentions {len(names)} symbols,")
    print(f"   so there are 2^{len(names)} = {2 ** len(names)} possible caves "
          f"to consider.")

    # ---------- B: how many caves survive ------------------------------
    print("\n[B] Throwing away the impossible caves")
    survivors = [m for m in all_models(names)
                 if all(evaluate(s, m) for s in knowledge_base)]
    print(f"   caves considered : {2 ** len(names)}")
    print(f"   caves that fit everything the agent knows : {len(survivors)}")

    print("\n   Here they are, written as the pits each one claims:")
    pits = pit_symbols(names)
    print(f"\n   {'':6}" + "".join(f"{p:>6}" for p in pits))
    for i, model in enumerate(survivors, 1):
        row = "".join(f"{'PIT' if model[p] else '.':>6}" for p in pits)
        print(f"   {i:>4}. {row}")

    # ---------- C: reading the answer off the table -------------------
    print("\n[C] Now just read the columns")
    print("\n   P21 is '.' in every surviving cave  -> [2,1] is SAFE")
    print("   P12 is '.' in every surviving cave  -> [1,2] is SAFE")
    print("   P31 and P22 change from row to row  -> UNKNOWN")
    print("\n   But look again at P31 and P22 together: in every single")
    print("   row, at least ONE of them is a pit. The agent does not")
    print("   know which square is deadly, yet it knows to avoid both.")

    # ---------- D: the same thing, by the algorithm -------------------
    print("\n[D] The same answers, from entails()")
    questions = [
        ("no pit at [1,2]?", NOT("P12")),
        ("no pit at [2,1]?", NOT("P21")),
        ("no pit at [2,2]?", NOT("P22")),
        ("IS there a pit at [2,2]?", "P22"),
        ("pit in [3,1] or [2,2]?", OR("P31", "P22")),
        ("pit in BOTH [3,1] and [2,2]?", AND("P31", "P22")),
    ]
    print(f"\n   {'question':<30}{'KB |= it?':<12}{'the agent says'}")
    for label, query in questions:
        answer = entails(knowledge_base, query)
        says = "KNOWS it is true" if answer else "does not know"
        print(f"   {label:<30}{str(answer):<12}{says}")

    # ---------- E: not entailed is NOT the same as false --------------
    print("\n[E] The mistake to avoid")
    for query in [NOT("P22"), "P22"]:
        answer, checked, surviving, counter = entails(
            knowledge_base, query, report=True)
        print(f"\n   KB |= {show(query):<8} ?  {answer}")
        if counter:
            shown = "  ".join(f"{p}={'T' if counter[p] else 'F'}"
                              for p in pits)
            print(f"      a cave that fits everything but breaks it:")
            print(f"      {shown}")

    print("\n   Both answers are False. The agent cannot prove there is")
    print("   a pit at [2,2], and it cannot prove there is not one.")
    print("   That is UNKNOWN, and it is the correct answer - not a bug.")
    print("\n   A careless agent that treats 'cannot prove a pit' as")
    print("   'no pit' walks into [2,2] and dies.")

    # ---------- F: the cost, again ------------------------------------
    print("\n[F] What this cost us")
    answer, checked, surviving, _ = entails(
        knowledge_base, NOT("P12"), report=True)
    print(f"   models built and tested : {checked}")
    print(f"   models that survived    : {surviving}")
    print(f"   models thrown away      : {checked - surviving}")
    print(f"\n   We built {checked} caves to answer ONE question, and we")
    print(f"   threw {checked - surviving} of them away. On a 4x4 cave with")
    print("   around 32 symbols that is over 4 billion caves - per")
    print("   question.")
    print("\n   Parts 6 and 7 answer the same questions without ever")
    print("   building a single model.")
