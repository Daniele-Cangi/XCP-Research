# XVM

XVM is the first reference execution substrate for XCP.

Its purpose is to provide deterministic, bounded programmability inside the public Xbox application sandbox without relying on arbitrary native-code loading, JIT compilation, shell access, runtime shader compilation, or unrestricted operating-system authority.

> XVM does not remove the sandbox. It creates a programmable machine inside the sandbox.

## Why it exists

XCP needs a target that can execute work which was not hard-coded as one fixed application behaviour while still preserving explicit limits and verifiable authority.

On Xbox, that requirement led to a small virtual machine whose programs can be statically admitted before execution.

## Current XVM v2 shape

The current private reference implementation defines:

- 32-bit deterministic words;
- 16 registers;
- 26 admitted opcodes;
- typed memory views;
- structured conditionals;
- bounded loops;
- bounded function calls;
- explicit traps;
- static worst-case fuel analysis;
- deterministic snapshots and resume;
- SPMD lane context;
- canonical CPU execution;
- GPU differential execution paths.

These are properties of the current reference implementation, not requirements that every future XCP target must reproduce instruction-for-instruction.

## Admission before execution

A valid program is not admitted merely because its byte stream can be parsed.

The verifier checks the declared program against the active execution profile before the runtime trusts it. Current checks include bounds such as:

- admitted ISA version and capabilities;
- instruction and function limits;
- call-graph validity and maximum depth;
- bounded loop structure;
- structured-control ownership;
- typed-memory access rights and ranges;
- static worst-case fuel;
- artifact identity and execution bindings.

Work outside the admitted contract fails closed.

## Static fuel

Fuel is not only a runtime timeout.

For admitted XVM programs, the verifier can derive a worst-case execution bound from the structured program before execution. The runtime then consumes fuel as work executes.

This gives XCP two different protections:

1. reject a program whose declared execution budget cannot cover its static bound;
2. stop execution if the admitted runtime budget is exhausted.

## Snapshot and resume

XVM state can be serialized into a deterministic checkpoint and restored later under the correct execution binding.

The current research implementation binds resume state to identities such as the execution context and checkpoint sequence and rejects modified or incompatible state.

This is useful for long-running deterministic workloads and for XCP's broader evidence model: a resumed execution must still be attributable to the work that produced it.

## CPU and GPU

The CPU reference path is the canonical semantic authority in the current runtime.

GPU paths are used under explicit differential policies. A GPU result is not automatically trusted because it ran faster; the declared verification mode determines whether it must agree with CPU or another admitted implementation before publication.

This distinction matters because XCP treats execution backends as replaceable mechanics, while the result contract remains explicit.

## What XVM is allowed to do

XVM programs operate through declared virtual-machine capabilities.

The current public-Xbox profile deliberately excludes arbitrary host authority such as:

- native or host code injection;
- shell or process creation;
- broad filesystem access;
- XVM-owned sockets;
- credentials stored on Xbox;
- client-supplied native shaders;
- undeclared host effects;
- unbounded resource use.

Future capabilities can be added only as versioned, bounded contracts.

## Relationship to XCP

XVM is important, but XCP is larger than XVM.

```text
source software
    -> source observation
    -> semantic representation
    -> target lowering
    -> XVM program / target artifact
    -> admitted execution
    -> observation
    -> evidence decision
```

A future XCP target could use a different execution substrate and still conform to the XCP architecture if it preserves the required admission, identity, observation, and evidence boundaries.

## Current publication boundary

This repository documents XVM's architectural role and publishes bounded evidence about XCP executions. The production XVM source is not distributed here today.

The planned open-source platform extraction is intended to make the relevant specification and reference-runtime surfaces independently inspectable when they have been separated cleanly from the historical research repository.