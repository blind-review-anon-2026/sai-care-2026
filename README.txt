SAI-CARE-control-v4 — bounded executable verification

Run with Python 3.10+ (standard library only), from the source directory:
    python3 verification/verify.py
No network access, API key, patient data, or external package is required.
The command exits nonzero on an assertion failure and rewrites verification/results.json.

Files
policy.py: immutable state and decision records, intake constraints, ordered rules,
           finite-state enumeration. This is the policy abstraction, not a classifier.
control.py: synchronous in-memory compiler, scripted model candidate, validation gates,
            version-bound digest approval, author attribution, audit and release stubs.
verify.py: exhaustive bounded checks plus 23 fixture groups, with multiple subcases.
results.json: actual output produced for this revision.

Domain
4 actors × 4 operations × 2 phases × 11 task labels × 4 risk labels × 2 statuses
× 2^4 Boolean predicate valuations = 45,056 raw tuples.
Four Boolean dimensions: scope prohibition, scope resolution, readiness metadata,
and professional route configuration. Consistency filtering leaves 8,848 states:
- NA iff operation is not transform;
- unknown task implies uncertain status;
- transformation with unassessed risk implies uncertain status;
- non-transformations use resolved status;
- owner requests use execute only.
Permission and readiness predicates are abstract inputs. Both prohibited and resolved
may be true: a resolved permission can be a denial. Concrete documents, delegation
credentials, identities, histories and service configurations are not enumerated.
Rule counts retain route true/false even where the route is irrelevant; do not treat
counts as frequencies of real requests. They differ from the 8,736 in the review notes
because the notes do not define the same enumeration and consistency constraints.

Observed result
8,848 returned decisions; 10 reachable terminal rules; R11 has zero matches.
R1..R11: 3248, 4000, 800, 400, 192, 88, 8, 56, 24, 32, 0.
Zero first-match discrepancies, repeat-evaluation discrepancies, I2 routing violations,
non-owner/non-execute R9 states, or caregiver R10 states other than editing.
4,256 low/moderate-to-high strengthening pairs all select R1.
23/23 fixture groups pass. This is not a statistical performance estimate.

Interpretation and limits
The predicate-list comparison checks transcription and order; it is not an independent
proof of the intended requirements. Determinism concerns fixed structured inputs,
not repeated assessments of natural-language requests. I2 enumeration verifies the
policy routing implication; selected fixtures additionally observe no model calls.

Model outputs, assessment labels and semantic verdicts are scripted. In C19 the actual
selected source contains an injection string, but the injection verdict is supplied by
the fixture: only control-path containment is tested, not attack detection. Source
strings are placed in a data field; no real model receives or interprets them.
Derived parameters use versioned-item handles (default z1); preferences use pref:key
handles and metadata explicit item handles. All channels apply B minus X; the prototype does not
implement a real extractor or a complete derivation graph. Source versions and consent
snapshots are simplified. Flag evidence is a supplied reviewer verdict, not verified
semantic entailment. No GUI tests patient or clinician comprehension.

Journal and transport are in-memory stubs. Mutation hooks represent interstage changes
synchronously; they do not test concurrency, durable transactions, crash recovery,
network failure, retry protocols with third parties, or clinical quality. The dispatch
map tests one stable delivery identifier and exact bundle binding. Production-grade
identity, authorisation, canonicalisation and storage require separate implementations.
Passing these fixtures cannot establish universal compliance with invariants I1–I8.

Regression subcases added in v4
C2: both route modes and owner/model actors; fixed deployment-owned urgent-care message;
    no source sentinel in that message, and no processing or dispatch.
C5: finalised recipient-visible provenance included in the digest; detached approval
    record excluded from its own hash; text/recipient/label changes invalidate approval;
    audit failure publishes no approved labels. Successful dispatch preserves the bundle.
C16: provenance mutation between check and dispatch blocks release, as do existing
     version, scope and consent mutations. Repeated delivery ID still reconciles once.
C21: exclusions independently cover sources, parameters, enabled preferences and metadata;
     task-changing exclusions pause until reconfirmed; sentinel values do not leak.
     Unexcluded unauthorised channels block, and authorised included channels survive.
The number 23 counts fixture groups, not individual assertions or independent samples.
Urgent-care wording is a synthetic deployment-configuration fixture, not medical advice
or a clinically evaluated service configuration.

Traceability: what is checked, and what is not
I1: C1/C5/C6/C8/C12/C14/C16/C20 check representative in-memory authority, bundle-binding
    and dispatch paths. Identity services, real recipients and atomic distributed release
    are not implemented. Finalisation is one synchronous operation, not a transaction test.
I2: routing implication enumerated over all 8,848 states; C2/C11 observe no model calls.
    Assessment accuracy and every possible runtime trace remain outside the check.
I3: C1/C7/C9/C18/C20/C22 check scripted origin/lineage/flag/review gates; semantic truth
    and faithful real-model transformation are not tested.
I4: C3/C15/C17/C21/C23 check sample service gates and all represented compiler channels.
    The item model does not implement a full derivation graph or production middleware.
I5: C10 checks omission of a disabled setting; persistence, editing/deletion UI and
    preference-store behaviour are not implemented.
I6: C2/C7/C11/C13/C14/C19/C22 check selected no-dispatch paths. C19 supplies detection.
I7: C13/C16 exercise unavailable-journal and dispatch-record stubs. Real durability,
    crash recovery and transport acknowledgement are not tested.
I8: C4/C17/C21 check pauses without inferred consent and explicit narrowing. Timers,
    scheduled expiry and a production consent workflow are not implemented.

Repeat evaluation is only a regression check on fixed input, not an independent proof.
The ordered-predicate oracle shares the specification with the evaluator and is not an
independent validation of the chosen policy requirements. Universal trace conformance,
clinical validity and production readiness are not claimed.
