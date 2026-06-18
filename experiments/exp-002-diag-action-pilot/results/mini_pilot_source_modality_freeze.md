# Mini-Pilot Source Modality Freeze

Date: 2026-06-18

Decision: user approved all proposed final source modality labels.

Frozen artifact: `data/mini_pilot_source_modality_labels.jsonl`

| source_id | final label | primary evidence | joint |
|---|---|---|---|
| src_001 | audio_only | audio | no |
| src_002 | audio_only | audio | no |
| src_003 | video_only | video | no |
| src_004 | video_only | video | no |
| src_005 | audio_video_joint | audio+video | yes |
| src_006 | audio_video_joint | audio+video | yes |
| src_007 | video_only_control | video | no |
| src_008 | video_only_control | video | no |
| src_009 | audio_video_joint_conflict_candidate | audio+video | yes |
| src_010 | audio_video_joint_conflict_candidate | audio+video | yes |

Next gate: corrupted-instance gold review for 40 rows.
