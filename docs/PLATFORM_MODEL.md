# XCP Platform Model

XCP is being separated conceptually into a platform layer and a product layer.

The distinction matters because the platform should be implementable and testable by software that was not written by the original XCP project.

## Five architectural invariants

These properties define the direction of the platform more strongly than any current engine, language, or target.

### 1. Intent is separate from execution

The producer that decides what should happen is not automatically trusted with unrestricted authority on the target.

An AI agent, compiler, developer tool, or human-authored adapter may produce target work. The target receives an admitted artifact rather than the producer's full authority.

### 2. Execution must be admitted before it is trusted

Successful execution is not enough.

The target must be able to reject work whose operations, resources, capabilities, identity, or control structure fall outside the declared execution contract.

### 3. Source meaning and target mechanics are different layers

A source adapter captures meaning. A target adapter decides how much of that meaning can be represented under the destination's capabilities.

Source and target are not required to share an engine, runtime, language, or object model.

### 4. Execution and fidelity are separate decisions

A candidate can run and still fail to preserve the declared source behaviour.

XCP keeps operability, semantic fidelity, perceptual fidelity, and stronger equivalence claims separate.

### 5. Claims must not exceed evidence

Missing observation does not become success.

Unmeasured behaviour remains unmeasured. A bounded scenario result cannot silently become whole-program equivalence.

## Platform vs Studio

### XCP Platform

The platform is the reusable technical boundary. The intended public surface includes concepts such as:

- specifications and schemas;
- semantic representation;
- source-adapter contracts;
- target-adapter contracts;
- XVM and reference execution components;
- evidence contracts;
- conformance tooling;
- small reference examples.

### XCP Studio

Studio is a product surface built around the platform. It can contain:

- project UX;
- orchestration;
- guided workflows;
- operational dashboards;
- distribution tooling;
- product-specific integrations.

Studio does not define whether an implementation is XCP-compatible.

## Reference implementations are not the standard

Today:

```text
Godot        -> first reference source family
Xbox + XVM   -> first reference target
XCP Studio   -> first product orchestration surface
```

The architecture is successful only if those choices can eventually be replaced or extended without collapsing the model.

For example, an independent source adapter should be able to target XCP without modifying the Godot adapter. A second XVM implementation should be able to validate itself against the same execution contract rather than copying private code.

## Conformance direction

The planned open platform should make compatibility measurable.

Candidate conformance surfaces include:

```text
XCP Source Adapter Conformance
XCP Semantic Model Conformance
XVM v2 Conformance
XCP Target Adapter Conformance
XCP Evidence Conformance
```

Conformance should report bounded capability and coverage, not vague compatibility labels.

For example, an adapter may legitimately support a subset of semantic invariants. That subset should be explicit rather than advertised as complete engine support.

## Why the open-source repository will be new

The current private research repository is a laboratory. It contains historical experiments, product branches, Xbox operational tooling, generated evidence history, prototypes, and research paths that are not part of the stable platform contract.

The planned public repository will therefore be extracted into a clean structure rather than created by making the historical repository public.

A likely shape is:

```text
xcp/
  spec/
  runtime/
  semantic/
  adapters/
  evidence/
  conformance/
  sdk/
  examples/
  docs/
```

The exact layout may change before publication. The invariant is more important than the directory name: a third party should be able to understand where a new adapter, runtime, verifier, or conformance implementation belongs.

## Current status

XCP-Research remains the public architecture-and-evidence boundary while the implementation continues to evolve privately.

The open-source extraction is intentionally later than the research work. The goal is to publish stable contracts and reference components rather than export the entire history of the laboratory.