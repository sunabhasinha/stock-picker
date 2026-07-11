# ADR-0003: Fuzzy strategies are candidate-finders, never auto-executors

Context: The KB itself flags pattern recognition (RHS/CWH, Section 3.6)
and turnaround research (Strategy 7, Section 5.5) as fuzzier than the
indicator strategies and recommends human-in-the-loop.

Decision: Every signal from RHS, CWH, V10, and Strategy 7 sets
`requires_human_confirmation=True` — including SELLs. The tolerances the
KB leaves unquantified (neckline 2%, base 5%, pivot window 2, "near
lifetime high" 5%, turnaround drawdown 10%/20%) are OUR documented
defaults in code constants, not course rules — tunable, and flagged as
such in module docstrings. Strategy 7's LLM research provider must answer
UNCLEAR rather than guess, and open research questions ride along in the
signal for the human to finish.

Consequences: the system's output is a reviewed shortlist, not trades; a
future "auto-execute" feature would need to supersede this ADR explicitly,
which is exactly the friction intended.
