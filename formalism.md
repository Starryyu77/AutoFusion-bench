---
version: v2
last_updated: 2026-05-17
---

# Formalism

## Version History

- **v1** (2026-05-14): initial scaffold.
- **v2** (2026-05-17): reframed around diagnostic benchmark tasks for modality
  triage, cross-modal recovery, and budget-aware routing.

## Modalities

Let the available modality set be:

```text
M = {T, A, V}
```

where:

- `T` is text or transcript evidence,
- `A` is audio evidence,
- `V` is video or frame evidence.

For each source example `i`, the clean raw input is:

```text
x_i = (x_i^T, x_i^A, x_i^V, y_i)
```

where `y_i` is the downstream task label or answer.

## Corruption

A corrupted benchmark instance is:

```text
z_ij = C_j(x_i)
```

where `C_j` is a controlled corruption operator. For every modality
`m in M`, the corruption metadata is:

```text
c_ij^m = (status, type, severity, location)
```

Allowed statuses:

```text
clean, corrupted, missing, conflicting, unknown
```

Locations are modality-specific:

- text: token or character span,
- audio: timestamp interval,
- video: timestamp interval, frame interval, or region metadata.

## Task Outputs

For each corrupted instance `z`, a model may be evaluated on five outputs.

### T1: Modality Health Diagnosis

Predict the status and defect type for each modality:

```text
d_hat_m = f_diag(z, m)
```

### T2: Defect Localization

Predict the affected evidence location:

```text
l_hat_m = f_loc(z, m)
```

### T3: Cross-Modal Recovery

Predict whether missing or corrupted information is recoverable:

```text
r_hat = f_rec(z)
```

If recoverable, also predict a recovery map:

```text
rho_hat = (source_modality, source_location)
```

### T4: Budget-Aware Routing

A route is a non-empty modality subset:

```text
s subseteq M, s != empty
```

The seven possible text/audio/video routes are:

```text
T, A, V, TA, TV, AV, TAV
```

Each route has a cost:

```text
kappa(s) = cost of reading/listening/watching with route s
```

Given budget `B`, the route is legal iff:

```text
kappa(s) <= B
```

The model predicts:

```text
s_hat = f_route(z, B)
```

### T5: Final Task or Abstention

The model predicts either an answer or an abstention:

```text
a_hat in Y union {abstain}
```

Abstention is correct when the gold label marks the instance as unrecoverable or
insufficiently evidenced.

## Gold Annotation

Gold labels are split into mechanically generated and human-verified fields.

Mechanically generated fields:

- corrupted modality,
- corruption type,
- severity,
- text span,
- audio time range,
- video time/frame range,
- generated corruption seed.

Human-verified fields:

- recoverability,
- recovery source modality,
- recovery evidence location,
- oracle route,
- final answer under corruption,
- abstention label.

LLMs may produce candidate annotations, but unverified LLM output is not gold.

## Metrics

Diagnosis:

```text
per-modality F1, defect-type macro-F1
```

Localization:

```text
text span F1, temporal IoU, frame/region IoU where available
```

Recovery:

```text
recoverability macro-F1, source-modality accuracy, evidence hit rate
```

Routing:

```text
oracle-route match, budget violation rate, routing regret
```

Final task:

```text
accuracy, macro-F1, MAE, correlation, or task-specific score
```

Abstention:

```text
coverage-risk curve, false-abstention rate, false-answer rate
```

## Cost-Normalized Utility

For a model prediction under budget `B`, define:

```text
Score = TaskPerformance - lambda * Cost
```

where `Cost` may be measured as input token count, audio seconds, video frames,
wall-clock latency, memory, or API cost. The benchmark must state which cost
model is active for each leaderboard or table.

## Dataset Construction Algorithm

1. Select raw multimodal source clips with aligned text, audio, video, and task
   labels.
2. Generate controlled corruptions with reproducible scripts.
3. Record mechanical corruption metadata.
4. Human-verify recoverability, evidence source, oracle route, and abstention.
5. Build splits that balance source dataset, defect type, severity,
   recoverability, and budget level.
6. Evaluate baselines on all five task layers, not only the downstream answer.
