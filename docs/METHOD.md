# Method

XCP investigates whether a source observation and a constrained target observation can support a narrowly stated behavioral result without treating successful execution as proof of equivalence.

The public method has five steps:

1. Authorize and identify one source revision and one bounded scenario.
2. Observe the source and seal a scenario-specific evidence identity.
3. Execute the corresponding target candidate and seal its observation identity.
4. Compare only the declared observations under explicit metric and tolerance authority.
5. Admit the smallest claim supported by complete evidence; reject any wider claim.

The transformation between source evidence and target execution is outside the public boundary. Public verification neither reconstructs nor reruns it.

## Operability, fidelity, and equivalence

These are separate decisions:

- **Operability** means the declared target lifecycle completed.
- **Scenario evidence** means the selected observations were bound and compared.
- **Bounded support** means any measured divergence stayed within the declared authority for that scenario.
- **Global equivalence** requires complete independent coverage and is not inferred from a successful scenario or lifecycle.

## Calibration, validation, and holdout

- **Calibration** may be used to establish or check a declared comparison setup.
- **Validation** tests an independently declared scenario against that setup.
- **Holdout** remains separate from both and checks that a bounded conclusion survives an independently reserved scenario.

Snapshots must retain the partition recorded at measurement time. A later result cannot be moved between partitions or used to reinterpret an earlier snapshot.

## Decision rule

A bounded scenario result may be supported only when:

- source and target evidence are complete for that scenario;
- all scenario and evidence identities agree;
- the differential report is bound to those exact identities;
- the measured delta is evaluated against a declared tolerance;
- the differential report contains no unverified behavior in the admitted scope;
- the claim remains within the published allowlist.

Missing evidence, inconsistent identities, an out-of-tolerance result, or claim widening fails closed.
