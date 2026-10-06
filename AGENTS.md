# Agent instructions

Read `docs/architecture.md`, `docs/memory-contract.md`, and the assignment supplied by the operator before changing behavior.

## Engineering boundaries

- Preserve native Hermes authentication, tools, model resolution, approvals, skills, session controls, memory providers, and OMH evidence semantics.
- Use public extension interfaces. Check actual host capabilities; do not infer compatibility from a version string or monkey-patch private runtime fields.
- Keep runtime integration in `optchat_hermes`; keep archive and coordination logic in `optchat_core`.
- Retained originals, exact project state, immutable results, and observed effect receipts are separate contracts. Summaries cannot authorize actions or establish completion.
- Use one writer per profile, fsynced journal commands, fenced leases, bounded calls, and explicit uncertain-effect recovery.
- Use typed interfaces and native utilities. Keep prompts in static resources. Avoid duplicating native provider, shell, approval, messaging, or workspace implementations.
- Keep private state and credentials outside the checkout. Use fictional or generated fixtures. Public test output must contain no personal history or deployment credentials.

## Working method

- Define coherent implementation units and observable acceptance criteria. Verify a unit before its dependent work.
- Preserve other contributors' changes. Do not reset, clean, stash, or overwrite work you do not own.
- Test behavior and error/recovery boundaries. Do not add placeholder tests, source-text tests, or tests that merely echo constants.
- Record the exact checks exercised. Distinguish simulated contracts, live integration, and unsupported host capabilities.
- Run `python3 scripts/check_repository.py` and the relevant runtime checks introduced by the implementation.
- Clean up processes and temporary profiles started for verification.

## Publication

- Review the full staged tree and commit diff before pushing.
- Keep third-party copyright, license, and attribution notices when adapting code.
- Follow the operator's authorization for commits, pushes, releases, pull requests, and deployments. A coding assignment does not authorize publishing packages or changing a live personal assistant.
- Update documentation to describe verified behavior and usable commands. Make completion claims from observed evidence.
