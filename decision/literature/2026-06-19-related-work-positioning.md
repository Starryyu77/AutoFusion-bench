# Related-Work Positioning (2026-06-19)

> Status: Decision-Team positioning draft. Updates the 2026-06-08 story's
> related-work table with work found in the 2026-06-19 literature scan.
> Purpose: pin the defensible novelty core and draw explicit boundaries
> against the closest prior work before scaling the pilot.

## 0. Defensible core (say only this)

We do **not** claim first missing-modality / first modality-diagnosis /
first abstention / first AV-robustness benchmark. The one claim the
2026-06-19 scan could **not** find an existing match for:

> We decouple a model's **diagnosis** of unreliable audio-video evidence
> from its **action** on that diagnosis, and measure the gap with a
> conditional metric `P(policy_action_wrong | diagnosis_right)` plus a
> control where a fixed rule consumes the model's own frozen diagnosis.

Everything else (diagnosis, recoverability, routing, abstention, AV
corruption) is positioned as a **component the action layer is built on**,
not as a standalone novelty.

## 1. Boundary table

| Area | Representative work | What they cover | Our boundary |
|---|---|---|---|
| **Know-but-not-act gap** (closest on phenomenon) | Hidden in Plain Sight (arXiv 2506.00258) | MLLMs possess the perception/reasoning skill but fail to surface silently-wrong inputs; "gap between reasoning competence and behavioral compliance" in text/image | Same phenomenon, but we localize it to **audio-video corrupted evidence** with an explicit **route/recover/abstain action layer** and a conditional gap metric, not clarifying-question recovery |
| **Calibrated abstention under broken consensus** (closest on annotation) | OMD-Bench (arXiv 2603.27187) | Breaks modality consensus; human per-instance "do modalities suffice / should abstain" labels; calibrated abstention | We add the full chain diagnose→**recoverability**→route→act, and measure **acting against one's own diagnosis**, not abstention calibration alone |
| **AV trustworthiness / robustness** | AVTrustBench (arXiv 2501.02135); DAVE (arXiv 2503.09321) | AVTrustBench: 600K AV QA, adversarial + compositional + modality-dependency, response calibration under perturbation. DAVE: forces both modalities necessary, decomposes error into atomic subcategories | We do not claim AV-robustness novelty; we **reuse DAVE-style necessity filtering** as a construct-validity gate and test action, not aggregate accuracy/calibration |
| **AVQA robustness / debias substrates** | FortisAVQA + MAVEN (arXiv 2504.00487); MUSIC-AVQA-v2 debias (arXiv 2310.06238) | Rephrase + head/tail distribution shift to kill language shortcuts; debiased answer distribution | Candidate substrates that mitigate our shortcut risk; we cite them as data sourcing, not as our contribution |
| **Cross-modal conflict / inconsistency** | MMIR (arXiv 2502.16033); CrossCheck-Bench (arXiv 2511.21717); XModBench (arXiv 2510.15148) | Detect/resolve image-text conflicts and cross-modal consistency | We target temporal AV degradation + recoverability + **action after detection**, not conflict detection as the endpoint |
| **AVQA selective answering** | Knowing When to Answer (arXiv 2602.04924) | Adaptive confidence refinement for reliable AVQA (when to answer) | Abstention is one action in our policy; we additionally test route + recovery and the diagnosis-action coupling |
| **Trust / uncertainty assessment** | FESTA (arXiv 2509.16648); LLM cascades w/ early abstention | Sampling-based trust scores; cost-aware abstention | Methods/scores, not an evidence-governance evaluation protocol |
| **Missing-modality robustness** (carried from prior notes — verify) | MissMAC-Bench, MissBench, UMQ, SMCIR | Final-task robustness or sample-level diagnosis+recovery under missing/noisy modalities | We evaluate explicit governance behavior + action, not final-task robustness |
| **Budgeted modality selection** (carried — verify) | MOSEL, MMR-Bench, AdaLLaVA | Model/modality selection under cost | Routing is our action layer tied to diagnosed reliability, scored by regret + diagnosis-action consistency |
| **AV/Video MLLM eval** | Video-MME; AVHBench (arXiv 2410.18325) | Broad video / AV understanding or hallucination | We target unreliable evidence + diagnosis-to-action, not broad capability |

## 2. The two papers that most threaten the framing

1. **Hidden in Plain Sight (2506.00258)** already demonstrates the
   competence-vs-compliance gap in MLLMs. It is the best citation that the
   phenomenon is real and important, *and* the strongest "you're not first"
   risk. Defense: it is text/image, single-shot, no AV corruption, no
   route/recover action layer, no conditional gap metric. We must cite it as
   motivation and explicitly state what we add.
2. **OMD-Bench (2603.27187)** already has human "modalities suffice / should
   abstain" labels and breaks modality consensus. Defense: it is
   abstention-calibration-centric; it does not score recoverability routing or
   the act-against-own-diagnosis gap, and (now verified, §5) has no
   frozen-diagnosis fixed-rule control.

If a reviewer combined these two, they would land near us. So the headline
**must** be the conditional decomposition + fixed-rule control, not "we test
abstention on broken AV."

## 3. Verification status

- Full text / abstract directly verified this session: DAVE (2503.09321), Hidden
  in Plain Sight (2506.00258), **OMD-Bench (2603.27187)** and **AVI-Bench
  (2606.07643)** full text (see §5).
- Title + arXiv id seen in search listings, abstract not opened: AVTrustBench,
  FortisAVQA/MAVEN, MUSIC-AVQA-v2 debias, MMIR, CrossCheck-Bench,
  XModBench, Knowing-When-to-Answer, FESTA, AVHBench.
- Carried from prior project notes, **not** re-found in this scan — verify
  before citing in the paper: MissMAC-Bench, MissBench, UMQ, SMCIR, MOSEL,
  MMR-Bench, AdaLLaVA.

## 4. To do before paper related-work freeze

- ~~Open and verify OMD-Bench / AVI-Bench full text~~ — done 2026-06-19, see §5.
- Re-verify or drop the "carried from prior notes" entries.
- Confirm whether any of these score *acting on stated diagnosis*; if none do,
  state that explicitly as the gap.

## 5. OMD-Bench / AVI-Bench full-text verification (2026-06-19)

### OMD-Bench (2603.27187, Al Nazi et al.; UC Riverside / UMBC / QCRI) — closest neighbor, NOT a collision on the core

Verified scope: **trimodal** (video + audio + **text**, all three as evidence),
27 anchors / 255 base QA pairs / factorial `2^3 = 8` corruption conditions →
4,080 instances. Corruption = **semantic substitution** (replace a modality
with a *different* anchor's content to create conflict/dissonance), evaluated
for (a) less-confounded modality-reliance attribution and (b) **calibrated
abstention**, with human per-instance "do the modalities suffice / is
abstention appropriate" labels. Ten omni models, zero-shot + CoT.

- **Real overlaps:** the human suffice/abstain labels; controlled corruption to
  isolate modality contribution; the over-/under-abstention finding (overlaps
  our `false_answer` / `false_abstention` metrics).
- **Confirmed gaps — our defensible core survives:** no recoverability-from-
  other-modality label; no evidence **routing** action; no diagnosis-to-action
  gap / `conditional_policy_failure`; no fixed-rule-on-frozen-diagnosis control.
  Its endpoint is abstention *calibration* (confidence vs correctness), not
  *acting consistently with one's own stated diagnosis*. Its corruption is
  *substitution*, not perceptual *degradation* (blur/occlusion/noise/mute) on
  real synchronized media.
- **Strategic implication:** OMD-Bench already does the trimodal (text-as-
  evidence) corrupt design we **deferred** to Phase 7. Do NOT frame the future
  text extension as "first trimodal evidence benchmark"; differentiate by
  degradation-vs-substitution and action-vs-calibration. Lead the paper with
  CPF + rule_lift, NOT abstention rates.

### AVI-Bench (2606.07643, Wang et al.; 01 Jun 2026) — low threat, not a competitor

Verified scope: a cognitively-inspired AV **capability** benchmark across
perception / understanding / reasoning, plus AVI-Bench-PriSe (primitive
audio-visual sensation on low-semantic stimuli for generalization), with a
four-level AVI taxonomy. No unreliable-evidence / corruption-governance /
abstention / diagnosis-to-action content.

- **Disposition:** move to the "broad omni-MLLM AV eval" bucket with Video-MME /
  AVHBench. While here, also cite the omni-eval neighbors OMD-Bench surfaces:
  OmniBench, AV-Odyssey, WorldSense, UNO-Bench.
