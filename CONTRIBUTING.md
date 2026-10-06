# Contributing

Contributions should preserve the architecture's ownership and memory contracts. Read [the architecture](docs/architecture.md) and [memory contract](docs/memory-contract.md) before changing those boundaries.

## Scope and review

Keep each pull request focused on one coherent behavior. Explain the concrete problem, resulting behavior, and the evidence that verifies it. For architectural changes, include the tradeoff and affected contracts so maintainers can assess the proposal.

AI-assisted contributions follow the same standard: the contributor reviews the full diff, understands the behavior, and runs the relevant checks. Include at least one sentence in your own words explaining what changed and why. Do not submit raw agent transcripts as the explanation.

Use conventional commit subjects such as `feat(memory): retain payload references` or `fix(runtime): reconcile interrupted attempts`. Link an existing issue when relevant; an issue is not required for a focused contribution.

## Validation

Run the repository checks:

```sh
python3 scripts/check_repository.py
```

Behavioral changes must also exercise the affected runtime contract. Add tests for externally observable transformations, isolation, state transitions, malformed inputs, and regression paths. Fault-injection tests should verify recovery without repeating effects. Compile/type guarantees belong in type checking rather than runtime placeholder assertions.

Keep fixtures synthetic and full-suite safe. Restore spies, configuration, environment changes, and temporary resources after each test. Use isolated Hermes profiles; do not run tests against a personal memory store or live gateway.

CI uses read-only permissions and SHA-pinned actions. Dependency updates should preserve those controls. Follow [GitHub's secure workflow guidance](https://docs.github.com/en/actions/reference/security/secure-use).

## Sensitive data

Do not submit credentials, real transcripts, personal-memory exports, native state databases, local deployment details, or private backups. Describe security-sensitive findings through [private reporting](SECURITY.md).

## Licensing and conduct

Contributions intentionally submitted for inclusion are licensed under [MIT](LICENSE). Preserve all applicable third-party notices and obtain the right to submit adapted material. A CLA or DCO is not required.

Follow [the code of conduct](CODE_OF_CONDUCT.md). Maintainers review correctness, evidence, clarity, and maintainability.
