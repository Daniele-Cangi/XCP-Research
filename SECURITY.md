# Security

This repository is intended to be safe to clone and verify offline. The verifier reads only the selected snapshot and repository-local schemas. It does not open network connections, invoke private tooling, contact a console, or execute snapshot content.

Run the publication audit before proposing a release:

```bash
python verifier/audit.py .
```

The audit rejects symlinks, unregistered non-text files, local paths, IP addresses, credential-shaped assignments, authorization headers, pairing values, and key or certificate blocks. The five public WebP/PNG captures under `assets/showcase/` and `assets/social-preview/` are accepted only when their paths, byte counts, SHA-256 digests, and Git blob identities match the exact allowlist in `verifier/audit.py`. Missing or altered captures and any other binary file fail the audit. This is a narrow automated guard, not a substitute for human disclosure review.

When reporting a vulnerability, do not attach private evidence, credentials, raw traces, proprietary assets, or device details. Describe the issue using the smallest synthetic reproducer possible.
