# XCP Research Evidence

XCP Research is a compact, public evidence surface for one bounded experiment. It shows how an authorized source observation, a constrained target observation, and a differential decision can be bound and checked without publishing the private transformation mechanism between them.

The publication rule is simple: **publish the proof boundary, not the implementation boundary**.

## Snapshot overview

![Scientific overview of the XCP Studio bounded validation pipeline](assets/xcp-studio-validation-overview.svg)

Public evidence surface for bounded source-to-target validation.

## Snapshot 001

The first snapshot records the historical `movement-left` validation scenario from a three-scenario motion study:

- source and target observations are bound to the same scenario identity;
- the constrained target execution completed its declared lifecycle;
- one trajectory divergence was measured;
- its historically reported magnitude was `0.052083984375` normalized cell;
- the canonical artifact carried the higher-precision decimal `0.052083984375000725`;
- the declared absolute tolerance was `0.1` normalized cell;
- the divergence was non-significant within that authority;
- the bounded scenario result was supported;
- global equivalence was not authorized.

The higher-precision value above is preserved rather than silently rounded. It does not change the historical bounded decision.

## Evidence flow

```text
AUTHORIZED SOURCE
       |
       | observe
       v
SOURCE EVIDENCE
       |
       v
+----------------------------+
| PRIVATE XCP TRANSFORMATION |
+----------------------------+
       |
       v
TARGET EXECUTION
       |
       | observe
       v
TARGET EVIDENCE
       |
       | compare
       v
BOUNDED EVIDENCE DECISION
```

The private block is deliberate. This repository describes what crosses the boundary and how published evidence is checked, not how source behavior is interpreted or transformed.

## Verify offline

Python 3.11 or newer is sufficient; there are no third-party runtime dependencies.

```bash
python verifier/verify.py snapshots/001-g2-motion-validation
python -m unittest discover -s tests -v
python verifier/audit.py .
```

Verification establishes integrity and internal consistency for the checked-out bytes. Authenticity still depends on obtaining the repository or release identity through a trusted channel.

Read [NON_CLAIMS.md](NON_CLAIMS.md) before interpreting the snapshot. The method, evidence contract, and immutability policy are in `docs/`.

## License

Original repository content is licensed under Apache License 2.0. No Minilens source, asset, trace, binary, or other third-party material is redistributed here; only factual identities and sanitized measurements are included.
