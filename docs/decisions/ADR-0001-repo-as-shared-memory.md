# ADR-0001: The repo is the shared memory (context-layer system)

Context: The project will grow to multiple contributors using DIFFERENT
LLM agents. Context must be model-agnostic, versioned, reviewable, and
must not rot into a separate wiki.

Decision: All agent/human context lives in the repository as markdown,
organized in layers (see AGENTS.md "Context layers" table): constitution
(AGENTS.md), intent (KB + docs/specs), decisions (docs/decisions), map
(MODULE.md per package), gates (tests + CI), learning loop (journal.md).
Git is the sync protocol. Vendor files (.claude/, .cursor/) are thin
adapters, never the home of content. Context files change only via
reviewed PRs; a code change updates the context it invalidates in the
SAME commit (CI-enforced drift check).

Judgment call recorded: CLAUDE.md predates this system and carries rich
build history — it is KEPT as the Claude adapter/extended map rather than
gutted, with AGENTS.md as the authority on conflicts. Revisit if the two
drift.

Consequences: any agent brand can orient from a cold start; onboarding is
a read-path over these layers rather than a document someone maintains;
the cost is the same-commit doc discipline, which CI now enforces.
