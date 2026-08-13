# XCP Studio — Public Research Evidence

**XCP Studio is a software creation and source-to-target adaptation platform for Xbox Series hardware.**

It supports two connected paths: creating new interactive software from an idea or prompt, and experimentally adapting authorized source software to a constrained Xbox runtime. In both cases, XCP turns the input into an editable project, builds a deterministic runtime bundle, executes the result on the target, observes what actually happened, and keeps the outcome measurable, versioned, and reversible.

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

The active XCP system uses a common project contract across visual tools, IDE workflows, and external agents. It can:

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

This repository publishes selected historical evidence, verification contracts, sanitized measurements, and bounded research snapshots so that public results can be checked independently without publishing the machinery that produced the candidate target.

The publication rule remains:

> **publish the proof boundary, not the implementation boundary.**

Each snapshot declares its measured scope, evidence contract, and decision authority explicitly. The public evidence can therefore be inspected on its own terms even as the active private system continues to evolve.

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

The private block may evolve. The public contract is about what enters the comparison, what evidence comes back from the target, and what conclusion that evidence supports.

## Snapshot 001 — measured motion preservation

The first public snapshot records the historical `movement-left` validation scenario from a three-scenario motion study.

It shows a concrete version of the XCP method: bind one source behavior and one target behavior to the same scenario, execute the target, measure both, and make a bounded decision from the observed divergence.

For this snapshot:

- source and target observations are bound to the same scenario identity;
- the constrained target execution completed its declared lifecycle;
- one trajectory divergence was measured;
- its historically reported magnitude was `0.052083984375` normalized cell;
- the canonical artifact carried the higher-precision decimal `0.052083984375000725`;
- the declared absolute tolerance was `0.1` normalized cell;
- the divergence was non-significant within that authority;
- the declared `movement-left` scenario was supported under the frozen snapshot contract.

The higher-precision value is preserved rather than silently rounded. It does not change the historical bounded decision.

![Scientific overview of the XCP Studio bounded validation pipeline](assets/xcp-studio-validation-overview.svg)

## Measured scope

Snapshot 001 evaluates one declared `movement-left` source-to-target scenario under a frozen measurement contract.

The historical motion study covered **6 of 182 hard invariant identities** and **6 of 182 perceptual invariant identities**. That measured coverage supports the declared scenario-level decision. A whole-project fidelity decision would require broader measured coverage across the remaining behaviors and invariants.

The authority of this snapshot is therefore precise: evidence for the recorded transition and scenario, under the contract and tolerance published with it.

## Verify the public evidence offline

Python 3.11 or newer is sufficient; there are no third-party runtime dependencies.

```bash
python verifier/verify.py snapshots/001-g2-motion-validation
python -m unittest discover -s tests -v
python verifier/audit.py .
```

Offline verification checks the integrity and internal consistency of the checked-out evidence. Source authenticity is established separately through the trusted repository or release identity.

The method, evidence contract, and immutability policy are documented in `docs/`.

## License

Original repository content is licensed under Apache License 2.0. No Minilens source, asset, trace, binary, or other third-party material is redistributed here; only factual identities and sanitized measurements are included.
