# Snapshot Policy

Published snapshots are immutable historical records.

- Measurements, source/target identities, partitions, tolerances, and claim boundaries in `001-*` must not be reinterpreted or silently replaced.
- Stronger or broader evidence requires a new `002-*` snapshot.
- A formatting correction or verifier fix may change repository code, but it must not change historical evidence values.
- If a historical artifact and a narrative summary differ in numeric representation, retain both representations and explain the discrepancy.
- Snapshot verification must fail when an evidence byte changes, a binding breaks, a differential contradicts its measurement, or a claim widens.
- Removed or superseded private systems do not invalidate the historical statement; they also do not expand it.

Before release, run the unit tests, snapshot verifier, publication audit, dependency check, and human reverse-engineering review.
