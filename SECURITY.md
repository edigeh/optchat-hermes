# Security policy

## Report a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/edigeh/optchat-hermes/security/advisories/new) for vulnerabilities, credential exposure, personal-memory disclosure, or unsafe execution paths.

Include a minimal synthetic reproduction, affected revision, expected and observed behavior, impact, and a proposed correction when available. Keep real credentials, personal history, and private archives out of the report. Maintainers may request a sanitized artifact through the private thread.

## Security boundaries

The architecture relies on authenticated principal bindings, audience-scoped memory grants, native approvals and sandboxing, one archive writer, fenced execution leases, and verified effect recovery. Application memory scopes do not establish operating-system isolation. Host integrations must state which native isolation controls they exercise.

Contributions changing authentication, archive capture, retrieval grants, plugin loading, backups, effect execution, or process recovery must include tests for the relevant negative and failure contracts.

## Supported material

Maintainers evaluate reports against the repository's default branch and identified upstream compatibility baselines. Dependency or upstream findings should identify the responsible component so the correction can reach its owner.
