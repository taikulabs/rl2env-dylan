**feat(cli): add kanban swarm topology helper**

Salvages #26791 by @Niraven.

Adds `hermes kanban swarm` to create a durable Kanban Swarm v1 graph: a completed root/blackboard card, parallel worker cards, a verifier gated on all workers, and a synthesizer gated on the verifier. Stores shared swarm blackboard updates as structured JSON comments on the root card.

Self-contained — new `hermes_cli/kanban_swarm.py` module + CLI wiring + 3 unit tests (passing).

Original branch had a small conflict on the kanban.py imports block; resolved by keeping both imports. Authorship preserved via rebase merge.