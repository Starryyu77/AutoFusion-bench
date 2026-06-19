# Mini-Pilot Source Modality Review

Date: 2026-06-18

Status: owner confirmed and source labels frozen.

User approved all proposed final source modality labels on 2026-06-18. This freezes source-level modality labels only; corrupted-instance labels still require review before scorer gold.

## Frozen Label Counts

| final_source_label | count |
|---|---:|
| audio_only | 2 |
| audio_video_joint | 2 |
| audio_video_joint_conflict_candidate | 2 |
| video_only | 2 |
| video_only_control | 2 |

## Frozen 10-Source Table

| source_id | candidate_bucket | final_source_label | primary evidence | joint? | status |
|---|---|---|---|---|---|
| src_001 | audio_necessary | audio_only | audio | no | frozen |
| src_002 | audio_necessary | audio_only | audio | no | frozen |
| src_003 | video_necessary | video_only | video | no | frozen |
| src_004 | video_necessary | video_only | video | no | frozen |
| src_005 | audio_video_joint | audio_video_joint | audio+video | yes | frozen |
| src_006 | audio_video_joint | audio_video_joint | audio+video | yes | frozen |
| src_007 | corrupted_irrelevant_control | video_only_control | video | no | frozen |
| src_008 | corrupted_irrelevant_control | video_only_control | video | no | frozen |
| src_009 | cross_modal_conflict | audio_video_joint_conflict_candidate | audio+video | yes | frozen |
| src_010 | cross_modal_conflict | audio_video_joint_conflict_candidate | audio+video | yes | frozen |

## Next Step

Proceed to corrupted-instance review for the 40 mini-pilot rows. Do not treat `mini_pilot.local.jsonl` as final scorer gold until each corrupted instance has reviewed answerability, recoverability, oracle route, abstention, confidence, and `instance_decision`.
