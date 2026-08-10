# Security

This repository is intended to be safe to clone and verify offline. The verifier reads only the selected snapshot and repository-local schemas. It does not open network connections, invoke private tooling, contact a console, or execute snapshot content.

Run the publication audit before proposing a release:

```bash
python verifier/audit.py .
```

The audit rejects symlinks, non-text files, local paths, IP addresses, credential-shaped assignments, authorization headers, pairing values, and key or certificate blocks. This is a narrow automated guard, not a substitute for human disclosure review.

When reporting a vulnerability, do not attach private evidence, credentials, raw traces, proprietary assets, or device details. Describe the issue using the smallest synthetic reproducer possible.
