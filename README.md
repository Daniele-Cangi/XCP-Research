# XCP Studio — Public Research Evidence

**XCP Studio is a creative software system for building, adapting, running, and validating interactive software on Xbox Series hardware.**

It connects PC-side creation and agent tooling to a bounded Xbox runtime. New work can begin from an idea or prompt; source-adaptation research can begin from authorized source software. XCP turns that input into an editable project, builds a deterministic runtime bundle, executes it on Xbox, observes what actually happened, and keeps the result versioned and reviewable.

```text
IDEA / PROMPT / AUTHORIZED SOURCE SOFTWARE
                    |
                    v
             EDITABLE XCP PROJECT
                    |
                    v
          DETERMINISTIC RUNTIME BUNDLE
                    |
                    v
              XBOX EXECUTION
                    |
          +---------+---------+
          |                   |
          v                   v
   STATE / LOGS / ERRORS   FRAME CAPTURES
          |                   |
          +---------+---------+
                    |
                    v
       COMPARE / REVISE / REPLAY / ROLLBACK
```

## What XCP actually does

XCP is not just an Xbox compute probe and not just a verification format.

The broader private system is being developed as a creative platform with a common project contract for people, visual tooling, IDE workflows, and external agents. That platform can:

- create structured interactive software from an idea or prompt;
- build deterministic, hash-bound project bundles;
- install, update, activate, launch, observe, version, and roll back those bundles on Xbox;
- expose graphics, UI, audio, state, behavior, storage, and bounded compute through one host contract;
- return structured errors and evidence instead of treating a successful build as proof that the result is correct;
- study **source-to-target adaptation** by taking authorized source software, producing a target representation, running it on Xbox, and comparing measured target behavior against source evidence.

That last point matters: XCP does not treat “it compiled” or “it looks similar” as source fidelity. Source adaptation is accepted only inside the evidence boundary actually measured. When the evidence is insufficient, the result stays partial or fails closed.

XCP is therefore best understood as a software creation and adaptation system with execution built into the validation loop:

> **build it, run it on the target, observe it, compare it, and only then decide what the result proves.**

For the broader product context, see [xcpstudio.com](https://xcpstudio.com/).

## Why this repository exists

`XCP-Research` is the public evidence surface of XCP Studio. It is intentionally **not** a mirror of the private transformation engine or the current engineering frontier.

This repository publishes selected historical evidence, verification contracts, sanitized measurements, and bounded research snapshots so that a public claim can be checked independently without publishing the machinery that produced the candidate target.

The publication rule remains:

> **publish the proof boundary, not the implementation boundary.**

That means the public repository may lag behind the active private system. A snapshot proves only the scope declared by that snapshot; it should never be read as a claim that arbitrary software can already be translated automatically or that source and target are globally equivalent.

## Source-to-target validation

The public validation model is deliberately simple to understand:

```text
AUTHORIZED SOURCE SOFTWARE
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
      TARGET SOFTWARE
          |
          | execute on target
          v
      TARGET EVIDENCE
          |
          | compare
          v
   BOUNDED EVIDENCE DECISION
```

The private block may evolve. The public contract is about what enters the comparison, what evidence comes back from the target, and what conclusion that evidence is allowed to support.

## Snapshot 001 — measured motion preservation

The first public snapshot records the historical `movement-left` validation scenario from a three-scenario motion study.

It shows a small but concrete version of the XCP method: bind one source behavior and one target behavior to the same scenario, execute the target, measure both, and make a bounded decision from the observed divergence.

For this snapshot:

- source and target observations are bound to the same scenario identity;
- the constrained target execution completed its declared lifecycle;
- one trajectory divergence was measured;
- its historically reported magnitude was `0.052083984375` normalized cell;
- the canonical artifact carried the higher-precision decimal `0.052083984375000725`;
- the declared absolute tolerance was `0.1` normalized cell;
- the divergence was non-significant within that authority;
- the bounded scenario result was supported;
- global equivalence was not authorized.

The higher-precision value is preserved rather than silently rounded. It does not change the historical bounded decision.

![Scientific overview of the XCP Studio bounded validation pipeline](assets/xcp-studio-validation-overview.svg)

## What this snapshot does not claim

Snapshot 001 is evidence for one declared validation boundary. It does **not** establish:

- universal source-to-target translation;
- whole-program behavioral equivalence;
- arbitrary executable compatibility;
- a general-purpose transpiler for Xbox;
- unrestricted Xbox capabilities;
- that every current XCP capability is represented in this public repository.

Those boundaries do not make XCP smaller. They separate the product and research program from claims that have not yet been earned.

Read [NON_CLAIMS.md](NON_CLAIMS.md) for the snapshot-specific interpretation rules.

## Verify the public evidence offline

Python 3.11 or newer is sufficient; there are no third-party runtime dependencies.

```bash
python verifier/verify.py snapshots/001-g2-motion-validation
python -m unittest discover -s tests -v
python verifier/audit.py .
```

Verification establishes integrity and internal consistency for the checked-out bytes. Authenticity still depends on obtaining the repository or release identity through a trusted channel.

The method, evidence contract, and immutability policy are documented in `docs/`.

## License

Original repository content is licensed under Apache License 2.0. No Minilens source, asset, trace, binary, or other third-party material is redistributed here; only factual identities and sanitized measurements are included.
