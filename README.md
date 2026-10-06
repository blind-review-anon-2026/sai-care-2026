# Supplementary material — From Prompt to Policy

This repository accompanies the paper **“From Prompt to Policy: Controlling LLM Transformations in Healthcare Communication”**, submitted to the SAI-CARE 2026 workshop. It provides the supplementary document and an executable artifact for inspecting and reproducing the paper's bounded verification results. The repository is provided anonymously for peer review.

## Start here

**[Read the supplementary material (PDF)](./Supplementary%20Material.pdf)**

The supplementary document explains the verification abstraction, the enumerated state space, the control-path fixtures, reproduction instructions, and the scope and limitations of the checks. The main paper presents the architecture, policy rules, invariants, and conformance cases C1–C23; the supplement provides additional detail on how selected control properties are checked.

## What this artifact demonstrates

The paper proposes a policy-controlled architecture for LLM-assisted healthcare communication. It separates permission to process information from authority to release a resulting communication, and makes approval depend on the exact recipient-visible artifact, its provenance, recipients, and scope.

The executable artifact makes the policy rules and selected lifecycle controls inspectable. It combines a finite policy-state enumeration with synthetic conformance fixtures covering input restrictions, validation gates, approval, and release. It uses structured inputs and scripted model outputs so that the control decisions can be reproduced without an external model or service.

## Package contents

| File | Purpose |
| --- | --- |
| [Supplementary Material.pdf](./Supplementary%20Material.pdf) | Supplementary document describing bounded executable verification, reproduction, and limitations. |
| [verification/policy.py](./verification/policy.py) | State and decision records, well-formedness constraints, ordered policy rules, and finite-state enumeration. |
| [verification/control.py](./verification/control.py) | Synchronous, in-memory prototype of input compilation, validation, provenance finalisation, artifact-bound approval, and release controls. |
| [verification/verify.py](./verification/verify.py) | Executable bounded checks and the 23 conformance fixture groups C1–C23, including their subcases. |
| [verification/results.json](./verification/results.json) | Recorded machine-readable verification results; regenerated when the verification script runs. |
| [verification/README.txt](./verification/README.txt) | Detailed technical notes on the verification domain, fixture coverage, and assumptions. |

## Reproduce the results

**Requirements:** Python 3.10 or later. Only the Python standard library is used; no additional packages, API keys, patient data, or network access are required to run the artifact.

Download or clone this repository, open a terminal in the directory containing the `verification` folder, and run:

```bash
python3 verification/verify.py
```

The script exits with a nonzero status if an assertion fails and regenerates `verification/results.json`. To compare a new run with the supplied results, retain a copy of that file before running the script.

The supplied results report:

- **8,848 well-formed policy states**, obtained by filtering 45,056 raw combinations under the declared consistency constraints.
- **10 reachable terminal rules**; the defensive fallback R11 is not reached within this domain.
- **Zero violations in the reported checks**, including first-match consistency, repeat evaluation, selected authority and routing constraints, and high-risk precedence.
- **4,256 risk-strengthening pairs**, all selecting R1 after strengthening the risk to high.
- **23 of 23 conformance fixture groups passing**. Each group may contain multiple subcases.

These counts describe the specified finite abstraction and synthetic fixtures. They are not estimates of real-world request frequencies or model performance.

## Scope and interpretation

The artifact checks selected control properties under explicit assumptions. Assessment labels, model outputs, and semantic validation verdicts are scripted. In particular, the prompt-injection fixture tests containment after a supplied detection verdict; it does not evaluate injection detection or the behaviour of a real LLM.

The control prototype is synchronous and uses in-memory audit and delivery stubs. The checks do not establish clinical validity, semantic accuracy, production readiness, or universal conformance with all invariants across arbitrary executions. Distributed concurrency, durable storage, crash recovery, and real network delivery are outside the implemented abstraction.

For the precise relationship between the checks and invariants I1–I8, see the [supplementary PDF](./Supplementary%20Material.pdf) and the [technical verification notes](./verification/README.txt).
