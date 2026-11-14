# =====================================================================
# CS344L - AI Lab | Week 9 | PART 3 of 8
# Topic : SEMANTICS - what a sentence MEANS
# Teacher: Raja Faisal Umar
# Run    : python part3_semantics.py
# =====================================================================
# Part 2 gave us sentences. A sentence on its own has no truth value:
# "there is a pit at [2,1]" is not true or false until we say which
# cave we are talking about.
#
# A MODEL is one complete guess about the world: every symbol gets a
# True or a False. Nothing is left out.
#
#     {"P21": False, "P12": False, "B11": False, ...}
#
# Think of a model as ONE POSSIBLE CAVE. With 8 symbols there are
# 2^8 = 256 possible caves, and exactly one of them is the real one -
# the agent just does not know which.
#
# Given a model, every sentence becomes definitely true or definitely
# false. The function that works that out is called evaluate(), and it
# is the engine under everything in Parts 4 to 8.
# =====================================================================

from part2_syntax import (NOT, AND, OR, IMPLIES, IFF, show, is_symbol,
                          symbols_in, cave_knowledge_base)


# ---------------------------------------------------------------------
# THE ENGINE
# Six lines of meaning, one per shape. Read it slowly - the whole of
# propositional logic is in this one function.
# ---------------------------------------------------------------------
def evaluate(sentence, model):
    """Is this sentence true in this model? Returns True or False."""

    # A symbol: just look it up in the model.
    if is_symbol(sentence):
        return model[sentence]

    operator = sentence[0]

    # NOT: flip whatever is inside.
    if operator == "not":
        return not evaluate(sentence[1], model)

    # The rest all have a left and a right side. Work both out first.
    left = evaluate(sentence[1], model)
    right = evaluate(sentence[2], model)

    if operator == "and":
        return left and right

    if operator == "or":
        return left or right

    # IMPLIES is the one that surprises people. "x => y" is FALSE in
    # one single case: x true and y false. Everywhere else it is TRUE.
    if operator == "=>":
        return (not left) or right

    # IF AND ONLY IF: true when both sides agree.
    if operator == "<=>":
        return left == right

    raise ValueError(f"unknown operator: {operator}")


def model_text(model, keys=None):
    """Write a model out as a short readable line."""
    keys = keys or sorted(model)
    return "  ".join(f"{k}={'T' if model[k] else 'F'}" for k in keys)


if __name__ == "__main__":
    print("PART 3: semantics - what a sentence means")
    print("=" * 66)

    # ---------- A: one model, several sentences -----------------------
    print("\n[A] One model - one possible cave")
    world = {"P21": True, "P12": False, "B11": True}
    print(f"   {model_text(world)}")
    print("   (in this imagined cave there IS a pit at [2,1], there is")
    print("    no pit at [1,2], and a breeze IS felt at [1,1])")

    print(f"\n   {'sentence':<26}{'true here?'}")
    for sentence in ["P21", "P12", NOT("P12"), AND("P21", "P12"),
                     OR("P21", "P12"), IMPLIES("P21", "B11"),
                     IFF("B11", OR("P21", "P12"))]:
        print(f"   {show(sentence):<26}{evaluate(sentence, world)}")

    # ---------- B: the same sentence, a different model ---------------
    print("\n[B] Change the model and the answers change")
    other = {"P21": False, "P12": False, "B11": True}
    print(f"   {model_text(other)}")
    rule = IFF("B11", OR("P21", "P12"))
    print(f"\n   {show(rule)}")
    print(f"      in the first model : {evaluate(rule, world)}")
    print(f"      in this model      : {evaluate(rule, other)}")
    print("\n   The second cave is IMPOSSIBLE: it claims a breeze with")
    print("   no pit next door. The rule returns False, which is how")
    print("   the agent will later throw such caves away.")

    # ---------- C: the implication truth table ------------------------
    print("\n[C] The one students always get wrong: x => y")
    print(f"\n   {'x':>6}{'y':>6}{'x => y':>10}   why")
    reasons = ["promise kept", "promise BROKEN",
               "promise not tested - still true",
               "promise not tested - still true"]
    for (x, y), reason in zip([(True, True), (True, False),
                               (False, True), (False, False)], reasons):
        m = {"x": x, "y": y}
        value = evaluate(IMPLIES("x", "y"), m)
        print(f"   {str(x):>6}{str(y):>6}{str(value):>10}   {reason}")

    print("\n   Think of 'x => y' as a PROMISE: if x happens, I promise")
    print("   y happens. The promise is only broken when x happened and")
    print("   y did not. If x never happened, you cannot accuse me of")
    print("   anything - so the sentence counts as true.")

    # ---------- D: three kinds of sentence ----------------------------
    print("\n[D] Three kinds of sentence")
    tests = [
        ("VALID - true in every model", OR("A", NOT("A"))),
        ("SATISFIABLE - true in some", AND("A", "B")),
        ("UNSATISFIABLE - true in none", AND("A", NOT("A"))),
    ]
    for label, sentence in tests:
        names = sorted(symbols_in(sentence))
        count = 0
        total = 2 ** len(names)
        for i in range(total):
            m = {n: bool((i >> j) & 1) for j, n in enumerate(names)}
            if evaluate(sentence, m):
                count += 1
        print(f"\n   {show(sentence):<16} true in {count} of {total} models")
        print(f"   {'':16} {label}")

    print("\n   A VALID sentence tells you nothing about the world -")
    print("   it is true whatever happens. An UNSATISFIABLE one is a")
    print("   contradiction. Part 7 turns every proof into a hunt for")
    print("   exactly that: a contradiction.")

    # ---------- E: testing the real knowledge base --------------------
    print("\n[E] Testing one guessed cave against the agent's knowledge")
    knowledge_base = cave_knowledge_base()
    every_symbol = set()
    for sentence in knowledge_base:
        symbols_in(sentence, every_symbol)
    every_symbol = sorted(every_symbol)

    guesses = [
        ("pit at [3,1] only", {"P31": True}),
        ("pit at [2,1] only", {"P21": True}),
        ("no pits anywhere", {}),
    ]
    for label, pits in guesses:
        model = {s: False for s in every_symbol}
        model.update(pits)
        model["B21"] = True                 # the agent really felt this
        model["B11"] = False                # and really felt no breeze here
        results = [evaluate(s, model) for s in knowledge_base]
        verdict = "POSSIBLE" if all(results) else "impossible"
        failed = [f"R{i + 1}" for i, ok in enumerate(results) if not ok]
        extra = "" if all(results) else f"  (breaks {', '.join(failed)})"
        print(f"\n   {label:<22}{verdict}{extra}")

    print("\n   The agent cannot see the cave, but it CAN throw away")
    print("   every cave that breaks one of its rules. Whatever is true")
    print("   in all the caves that survive is something it knows.")
    print("\n   That idea has a name - ENTAILMENT - and checking it by")
    print("   trying every model is Part 4 and Part 5.")
