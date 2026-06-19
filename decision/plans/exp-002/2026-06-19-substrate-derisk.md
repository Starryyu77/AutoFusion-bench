# Substrate De-Risking Assessment (2026-06-19)

> Status: Decision-Team draft. Addresses Risk 1 of the 2026-06-19 proposal
> (AVQA may be too easy / shortcut-solvable) before committing the 40-source
> pilot. Recommendation, not yet a frozen decision.

## 0. The risk, stated precisely

Three shortcut modes would each gut the benchmark:

1. **Question-only guessing** — answer inferable from question + options text
   with no media.
2. **Single-modality leakage on a "joint" item** — item labeled
   audio-video-joint but answerable from one stream alone.
3. **Artifact detection** — corruption is so visible the model infers the task
   from the noise pattern, not the evidence.

DAVE's stated motivation confirms (1)-(2) are real in existing AV benchmarks:
"existing benchmarks often suffer from strong visual bias — answers can be
inferred from visual data alone" (arXiv 2503.09321).

## 1. Candidate substrates

| Substrate | Strength for us | Weakness for us |
|---|---|---|
| **AVQA / AVQA-videos** (current) | Real-world scenes, breadth, available (HF `juyil/AVQA-videos`), supports single-modality buckets + irrelevant-corruption controls | Visual bias / question-only guessing; "joint" necessity not guaranteed |
| **DAVE** (arXiv 2503.09321) | **Forces both modalities necessary**; atomic error categories; built exactly to kill visual bias | Both-necessary by design → poor for single-modality and irrelevant-corruption rows; smaller; diagnostic flavor |
| **FortisAVQA + MAVEN** (arXiv 2504.00487) | First AVQA robustness set; rephrase + head/tail shift kills language shortcuts | Music domain → narrow scenes; built for robustness eval, not modality-necessity split |
| **MUSIC-AVQA-v2 / debias** (arXiv 2310.06238) | Debiased answer distribution | Music domain; same narrowness |

## 2. Key realization: no single substrate fits all buckets

Our buckets need **opposite** properties:

- audio-only / video-only / irrelevant-corruption-control rows need
  **single-modality-necessary** items (corrupt the necessary modality →
  unanswerable; corrupt the other → no effect).
- audio-video-joint / conflict rows need **both-modalities-necessary** items.

DAVE is ideal for the second and wrong for the first. AVQA can supply the
first but needs a hard gate. So the answer is not "switch substrate" but
"source each bucket from where its property is guaranteed."

## 3. Recommendation

1. **Keep AVQA** for single-modality buckets and irrelevant-corruption
   controls, but **strengthen the source gate** with an explicit
   question-only-guess screen: try to answer each candidate from question +
   options text alone (a text-only LLM pass + a human spot-check); drop any
   item that is guessable. This directly closes shortcut mode (1).
2. **Add a DAVE-sourced tranche** for the audio-video-joint and conflict
   buckets, where "both modalities necessary" is exactly the property we want
   and is already guaranteed by construction. This closes shortcut mode (2)
   for the hardest, most paper-critical rows.
3. **Hold FortisAVQA / MUSIC-AVQA-v2 as documented backup** (as the proposal
   already says) if joint/complementary samples are still too few after 1-2.
   Cite them as evidence we took AVQA bias seriously even if unused.
4. Artifact shortcut (3) is handled in the gold-freeze plan (silent-track mute
   fix + irrelevant-corruption control + generator-metadata baseline), not by
   substrate choice.

## 4. Why not just switch fully to DAVE

DAVE's both-modalities-necessary design removes our ability to build clean
single-modality and irrelevant-corruption rows, which the governance story and
the irrelevant-corruption control both require. DAVE strengthens the joint
bucket; it cannot carry the whole protocol.

## 5. Decision needed from TianYu

- Approve the "AVQA (gated) + DAVE joint tranche" split, or keep AVQA-only for
  the mini-pilot and revisit at the 40-source gate?
- Approve adding the text-only question-guess screen to the source gate?

## 6. Verification status

DAVE abstract verified this session (2503.09321). FortisAVQA (2504.00487) and
MUSIC-AVQA-v2 debias (2310.06238) seen in search listings; confirm domain fit
and licensing before sourcing.
