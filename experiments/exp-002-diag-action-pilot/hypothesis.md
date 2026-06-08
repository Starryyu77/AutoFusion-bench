---
id: exp-002
parent: null
status: planned
created: '2026-06-08'
hypothesis: >-
  MLLMs show a measurable diagnosis-to-action gap on unreliable audio-video
  evidence under textual queries: they may diagnose evidence damage but still
  route answer or abstain incorrectly.
related_claims: []
forked_from: null
fork_reason: null
drift_commit: null
naming:
  matrix_id: mat-002
  variable_id: var-002
  canonical_variable: diagnosis_to_action_protocol
  variant_value: audio_video_textual_query_pilot
  paper_label: Diagnosis-to-action pilot
---
# exp-002: diag-action-pilot

## Hypothesis

MLLMs show a measurable diagnosis-to-action gap on unreliable audio-video evidence under textual queries: they may diagnose evidence damage but still route answer or abstain incorrectly.

## What changed

- Added: AVQA_MUSIC_AVQA source selection
- Added: modality necessity labeling
- Added: controlled audio-video corruption manifest
- Added: human recoverability route abstention labels
- Added: diagnosis-only structured prompt
- Added: model action from frozen diagnosis
- Added: fixed rule from same frozen diagnosis
- Added: oracle route and oracle defect-location probes
- Modified: pilot scope narrowed to audio-video evidence governance under textual queries
- Modified: MELD demoted to diagnostic or control substrate
- Modified: budget routing reframed as constrained evidence selection
- Modified: final answer accuracy demoted to secondary metric

## Naming

- Matrix: mat-002
- Variable ID: var-002
- Canonical variable: diagnosis_to_action_protocol
- Variant value: audio_video_textual_query_pilot
- Paper label: Diagnosis-to-action pilot

## Success criteria

- self-inconsistency appears in at least 2 models and 10 cases
- conditional action failure exceeds 25 percent on a core subset
- fixed rule gives 5 to 10 point rule lift
- unrecoverable false-answer rate materially exceeds false abstention rate
- quality-only detector does not approach oracle
- recoverability annotation reaches at least moderate agreement

## Kill criteria

- fewer than 2 audio-video capable models after feasibility check
- AVQA or MUSIC-AVQA raw data cannot be staged legally
- question-only baseline solves most candidate items
- recoverability agreement kappa below 0.4
- quality-only route detector approaches oracle
- no clear diagnosis-to-action gap after 200 scored instances
