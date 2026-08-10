# Evidence Model

Each snapshot contains three small evidence summaries plus a manifest.

## Source summary

The source summary identifies the authorized external revision, the scenario partition, the canonical private trace identity, and whether observation completed for the selected scenario. It contains no trace events or interpretation structure.

## Target summary

The target summary binds the same scenario and source-trace identity to an opaque target project identity, worker artifact identity, lifecycle receipt identity, target-observation identity, and canonical target trace identity. It contains no package, protocol, capability-list, or worker implementation details.

## Differential report

The differential report binds the scenario, source trace, target trace, historical report, and root-cause evidence identities. It publishes only aggregate invariant counts, the measured trajectory delta, tolerance authority, classification, and bounded decision.

## Manifest

`manifest.json` binds every other snapshot file by relative path, byte length, and SHA-256. Its `manifest_sha256` is the SHA-256 of canonical JSON after removing that field. Canonical JSON uses UTF-8, sorted keys, no insignificant whitespace, and no ASCII escaping.

The manifest proves internal binding, not origin authenticity. Consumers should separately pin a trusted Git commit or release identity.

## Consistency graph

```text
manifest
  +-- source summary --+
  +-- target summary --+-- same snapshot / phase / scenario
  +-- differential ----+

source trace ----------> target source binding
source trace ----------> differential source identity
target trace ----------> differential target identity
scenario identity -----> all three evidence documents
```

All JSON schemas reject undeclared properties. The Python verifier applies the same strict contract without requiring an external schema library.
