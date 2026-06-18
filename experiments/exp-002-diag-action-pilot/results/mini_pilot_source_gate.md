# Mini-Pilot Source Gate
Date: 2026-06-18
## Gate Decision
All 10 clean source items pass the current source-quality gate based on user confirmation.
Confirmed source-level conditions:
- original audio/video are clean and usable;
- original media support the gold answer;
- answers cannot be obtained from question/options alone;
- no source has obvious ambiguity, excessive common-sense dependence, or unreliable gold answer.
This does not yet freeze corrupted-instance gold labels. It only clears the clean-source gate.
## Source Summary
| source_id | dataset | candidate_bucket | question | gold | gate | source modality consistency |
|---|---|---|---|---|---|---|
| src_001 | AVQA_HF_sample | audio_necessary | What are the people doing in the video? | Practice oral skills | accept | inconsistent (4 variants) |
| src_002 | AVQA_HF_sample | audio_necessary | What is the source of the sound in the video? | police car | accept | inconsistent (4 variants) |
| src_003 | AVQA_HF_sample | video_necessary | What is the source of the sound in the video? | Birdsong | accept | inconsistent (3 variants) |
| src_004 | AVQA_HF_sample | video_necessary | What are the people doing in the video? | Bowling | accept | consistent |
| src_005 | MUSIC-AVQA | audio_video_joint | Is the first sound coming from the right instrument? | yes | accept | inconsistent (4 variants) |
| src_006 | MUSIC-AVQA | audio_video_joint | How many instruments in the video did not sound from beginning to end? | one | accept | inconsistent (4 variants) |
| src_007 | AVQA_HF_sample | corrupted_irrelevant_control | What animal appears in the video? | fish | accept | inconsistent (2 variants) |
| src_008 | AVQA_HF_sample | corrupted_irrelevant_control | What numbers appear in the video? | twenty-seven | accept | consistent |
| src_009 | AVQA_HF_sample | cross_modal_conflict | What is the source of the sound in the video? | a car | accept | inconsistent (4 variants) |
| src_010 | AVQA_HF_sample | cross_modal_conflict | What are the people doing in the video? | Performing oral skills | accept | inconsistent (4 variants) |

## Remaining Issue: Modality Necessity
The annotation rows contain `source_modality_necessity`, including `audio_video_joint_required`. However, because the same source appears in four corrupted-instance rows, these source-level fields are not always consistent across the four rows.
Therefore, the next step is to resolve one source-level modality decision per source before freezing gold:
- audio-only / audio-necessary;
- video-only / video-necessary;
- audio-video joint;
- control / corruption-irrelevant;
- conflict candidate.

## Per-Source Modality Variants Observed

### src_001: audio_necessary
- 1 row(s): audio=necessary, video=irrelevant, joint=no
- 1 row(s): audio=necessary, video=supportive, joint=yes
- 1 row(s): audio=supportive, video=sufficient, joint=yes
- 1 row(s): audio=irrelevant, video=necessary, joint=no

### src_002: audio_necessary
- 1 row(s): audio=sufficient, video=supportive, joint=yes
- 1 row(s): audio=necessary, video=irrelevant, joint=no
- 1 row(s): audio=sufficient, video=necessary, joint=yes
- 1 row(s): audio=supportive, video=necessary, joint=yes

### src_003: video_necessary
- 2 row(s): audio=necessary, video=irrelevant, joint=no
- 1 row(s): audio=irrelevant, video=sufficient, joint=no
- 1 row(s): audio=irrelevant, video=necessary, joint=no

### src_004: video_necessary
- 4 row(s): audio=irrelevant, video=necessary, joint=no

### src_005: audio_video_joint
- 1 row(s): audio=necessary, video=necessary, joint=yes
- 1 row(s): audio=necessary, video=irrelevant, joint=no
- 1 row(s): audio=supportive, video=necessary, joint=yes
- 1 row(s): audio=irrelevant, video=necessary, joint=no

### src_006: audio_video_joint
- 1 row(s): audio=necessary, video=sufficient, joint=yes
- 1 row(s): audio=necessary, video=irrelevant, joint=no
- 1 row(s): audio=supportive, video=necessary, joint=yes
- 1 row(s): audio=irrelevant, video=necessary, joint=no

### src_007: corrupted_irrelevant_control
- 3 row(s): audio=irrelevant, video=necessary, joint=no
- 1 row(s): audio=irrelevant, video=irrelevant, joint=no

### src_008: corrupted_irrelevant_control
- 4 row(s): audio=irrelevant, video=necessary, joint=no

### src_009: cross_modal_conflict
- 1 row(s): audio=necessary, video=necessary, joint=yes
- 1 row(s): audio=necessary, video=irrelevant, joint=yes
- 1 row(s): audio=sufficient, video=necessary, joint=yes
- 1 row(s): audio=supportive, video=necessary, joint=yes

### src_010: cross_modal_conflict
- 1 row(s): audio=necessary, video=sufficient, joint=yes
- 1 row(s): audio=necessary, video=irrelevant, joint=no
- 1 row(s): audio=sufficient, video=necessary, joint=yes
- 1 row(s): audio=irrelevant, video=necessary, joint=no
