# CS344L Lab 9 — Knowledge-Based Agents I

**Student:** Hussnain Ahmad · **Roll No:** 242816 · **Course:** CS344L Artificial Intelligence Lab, Air University Islamabad · **Teacher:** Raja Faisal Umar

The eight part files provided in the Week 9 lecture (Propositional Logic), kept together in one folder — later parts import from earlier ones, so all eight must stay side by side. Plain Python only, nothing to install.

## Run

```bash
python part1_knowledge_base.py
python part2_syntax.py
python part3_semantics.py
python part4_truth_tables.py
python part5_entailment.py
python part6_cnf.py
python part7_resolution.py
python part8_compare.py
```

Part 8 takes a few seconds — it measures model checking running out of road as the cave grows.

## The eight parts

| File | What it does |
|---|---|
| `part1_knowledge_base.py` | Sets up the cave and shows why a reacting agent fails: a knowledge base (TELL / ASK) is needed to reason about unseen squares. |
| `part2_syntax.py` | Propositional sentences as Python data — symbols, NOT, AND, OR, IMPLIES, IFF. |
| `part3_semantics.py` | `evaluate()` — the truth of a sentence inside a model; change the model and answers flip. |
| `part4_truth_tables.py` | Truth tables: satisfiable, unsatisfiable, tautology, and the logic laws verified row by row. |
| `part5_entailment.py` | Entailment by model checking over all 128 caves; what is not entailed either way is honestly UNKNOWN. |
| `part6_cnf.py` | Converting any sentence to conjunctive normal form (clauses), the input resolution needs. |
| `part7_resolution.py` | Resolution: the same entailments as Part 5, proved by deriving the empty clause — no models built. |
| `part8_compare.py` | Model checking vs resolution as the cave grows: the models column doubles per symbol (2^n) while resolution's proof barely moves. |
