# Mini-Pilot Gold-Freeze Adjudication Plan (2026-06-19)

> Status: Decision-Team prep doc. AI agent prepared the rules, the media fix,
> and per-row recommended dispositions. **Gold freeze itself is TianYu's call**
> (per EXPERIMENT_CONSTITUTION). Recommendations below need confirmation
> against the actual media before `mini_pilot.gold.jsonl` is frozen.

## 0. Two blockers, in priority order

1. **Media bug (must fix before any model call).** The 5 `audio_mute`
   corrupted files have **no audio stream at all** (video-only). Noise-
   corrupted files correctly keep an `aac` audio stream. This is an
   input-contract inconsistency and an artifact shortcut (a model could infer
   "this is the mute condition" purely from "no audio stream").
2. **17 rows stuck in adjudication** (3 oracle-route, 1 unclear, 13 partial).
   Resolving these decides whether the headline set has enough non-trivial
   rows to show the gap (see headline-metric doc §4).

## 1. Media fix: re-encode mute as silent-present, not stream-absent

ffprobe confirmed (2026-06-19), all five video-only:
`src_001__音频静音`, `src_004__音频静音`, `src_006__音频静音`,
`src_007__音频静音`, `src_010__音频静音`.

**Decision:** `audio_mute` should mean *present-but-silent audio track*
(amplitude zeroed, same codec/sample-rate/duration as clean), not *audio stream
removed*. Rationale: (a) every corruption type then keeps the same
video+audio container, so "no audio stream" can't be a shortcut; (b) the omni
model still receives an audio channel and must *diagnose* it as silent, which
is the actual evidence-diagnosis skill; (c) it matches the data-spec example
(`modality_quality_status.audio = missing`, `makes_unanswerable`) at the label
level without changing the container contract.

Exact command (per file, non-destructive — writes `.fixed.mp4`):

```bash
ffmpeg -y -i clean/<src>.mp4 -map 0:v -map 0:a \
  -c:v copy -af volume=0 -c:a aac -shortest \
  corrupted/_audio_mute_fixed/<src>__音频静音.mp4
```

After ffprobe shows both `h264` + `aac` with `mean_volume ≈ -91 dB`, swap the
fixed files in and re-run the validator. Labels do **not** change.

## 2. Adjudication rules (apply in this order, then default to exclude)

| Rule | Condition | Disposition |
|---|---|---|
| **A. Irrelevant-corruption upgrade** | corruption hits a modality that is *irrelevant* to the question for this source (e.g. audio noise on a `video_only` source) | `answerable`; `recoverability=not_needed`; `corruption_relevance=answer_irrelevant`; `corruption_effect=no_effect`; `preferred_route=[clean modality]`. **Keep as headline — these are the false-alarm controls.** |
| **B. Clean-recovery upgrade** | corrupted modality is not the necessary one; another clean modality supports the gold answer | `answerable`; `recoverability=recoverable`; `recovery_source=[other]`; `preferred_route=[other]`. **Keep as headline — research-critical.** |
| **C. Necessary-modality degraded** | corruption hits the necessary modality | severe → `unanswerable`+`abstain=true` (headline, abstention test); mild but clearly usable → `answerable` w/ degraded route; genuinely borderline → exclude |
| **D. Oracle-route repair** | answerable but `preferred_route` empty | set route via A/B/C; if both modalities still required & usable → `[audio,video]`; if undecidable → exclude |
| **E. Unclear** | any `unclear` field | resolve by dominant evidence after media re-view; still unclear → exclude |
| **F. Default** | none of the above cleanly applies | `exclude_from_main` (preserves the existing partial→exclude reliability rule) |

## 3. Recommended dispositions for the 17 stuck rows

Inferred from question + gold + source-modality label; **confirm against media.**
"→ HEADLINE" means it should be rescued into hard scoring, not excluded.

### Oracle-route repair (3)
| Row | Source | Recommended | Rule |
|---|---|---|---|
| `src_005__视频轻度模糊` | av_joint | route=`[audio,video]` if joint still needed, else clean modality → HEADLINE | D |
| `src_005__音频轻度加噪` | av_joint | likely route=`[video]` (audio only mildly noisy) → HEADLINE | D/B |
| `src_006__音频重度加噪` | av_joint | severe audio + joint → likely `unanswerable`/abstain or exclude | D/C |

### Unclear (1)
| Row | Source | Recommended | Rule |
|---|---|---|---|
| `src_001__视频重度模糊` ("what are people doing", gold=Practice oral skills) | audio_only | video blurred but source is audio-only → answer recoverable from audio → `answerable`,`recoverable`,route=`[audio]` → **HEADLINE (prime gap case)** | E/B |

### Partial (13) — split by rule
**Likely irrelevant-corruption controls → upgrade to HEADLINE (Rule A):**
`src_007__音频重度加噪`, `src_008__音频轻度加噪` (audio corruption on `video_only` sources whose answer needs video).

**Likely clean-recovery → upgrade to HEADLINE (Rule B):**
`src_001__视频轻度遮挡`, `src_002__视频重度遮挡` (video corrupted, answer recoverable from audio on audio-only sources).

**Necessary-modality degraded / conflict — adjudicate severity (Rule C), several are the juiciest conflict rows:**
`src_002__音频重度加噪`, `src_003__视频重度模糊`, `src_007__视频轻度遮挡`,
`src_008__视频轻度模糊`, `src_009__视频轻度模糊`, `src_009__音频轻度加噪`,
`src_009__音频重度加噪`, `src_010__音频轻度加噪`, `src_001__音频轻度加噪`.

> Prioritize resolving the `src_009` / `src_010` conflict-candidate rows rather
> than excluding them — they are the highest-value rows for the gap metric.

## 4. Projected headline set after adjudication

- Currently clean headline candidates: 17.
- Rescuable via Rules A/B (controls + recovery): ~4-6 more.
- Net: ~21-23 headline rows, of which a meaningful share are non-trivial
  (recovery + irrelevant-control + conflict). Still small: treat the
  mini-pilot CPF as **existence evidence**, not a quotable rate (headline-metric
  doc §4). Quote CPF only at the 40-source pilot.

## 5. Decision checklist for TianYu (binary calls)

1. Approve the silent-present mute fix + swap? (y/n)
2. Approve Rule A upgrades (irrelevant-corruption rows → headline controls)? (y/n)
3. Approve Rule B upgrades (clean-recovery rows → headline)? (y/n)
4. For each `src_009`/`src_010` conflict row: usable-after-corruption or
   exclude? (per-row)
5. `src_006__音频重度加噪`: abstain-headline or exclude?

Once 1-5 are answered, the agent regenerates the export, runs the validator,
freezes `mini_pilot.gold.jsonl`, and runs diagnosis / real action / fixed-rule
control / scorer end to end.
