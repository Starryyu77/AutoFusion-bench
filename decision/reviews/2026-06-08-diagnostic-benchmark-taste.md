---
type: taste
target: "user-prompt: diagnostic benchmark direction for modality triage, cross-modal recovery, and budget-aware routing"
exp: null
created: 2026-06-08
---

# Research Taste Note: Diagnostic Benchmark

## One-sentence read

This is a taste-positive direction if it is treated as a diagnostic benchmark
for evidence use under unreliable modalities, but it becomes weak quickly if it
collapses into another missing-modality robustness dataset or a MELD-only
performance table.

## Concrete work

- Question/result: Should AutoFusion-Bench study whether MLLMs can diagnose
  damaged text/audio/video evidence, recover missing information from another
  modality, choose modalities under budget, and abstain when evidence is
  insufficient?
- Current evidence: The project has a proposal, formalism, reference pack, and
  prior `exp-001` MELD evidence showing that the older feature-level MELD line
  is operationally valid but not a positive benchmark-signal result.
- Desired claim: Existing MLLMs and multimodal models fail systematically on
  modality diagnosis, defect localization, recoverability, routing, or
  abstention under controlled perceptual defects.

## Taste axes

| Axis | Read | Why it matters |
|---|---|---|
| Important problem | strong | Real multimodal systems are not only asked to answer; they must decide which evidence is trustworthy and worth reading under cost. This is a real deployment problem, not only a benchmark artifact. |
| Common structure | strong | The work can represent a general structure: evidence reliability, compensation, and action selection under partial observability. That generalizes beyond sentiment datasets. |
| Right problem and attack | unclear | The stated problem is central, but the current attack could still become an easy proxy if it stays with text-dominant affective datasets or synthetic corruptions that are too obvious. |
| Story potential | strong | A good result would say: current MLLMs can fuse modalities, but do not reliably triage evidence when modalities degrade. That is a clean benchmark story. |
| Anomaly lens | unclear | The prior MELD negative signal is probably not a bug; it suggests the old dataset/protocol may be too text-dominant. The minimum validation is to test one non-affective audio/video dataset before scaling. |
| Social taste check | strong | This may look like engineering because it is a benchmark, corruption generator, and annotation schema. That should not be dismissed: good evaluation work often exposes a more important structure than another model tweak. |
| Courage check | risk | The important version requires raw audio/video MLLM evaluation and human-verified recoverability/evidence labels. Avoiding that by doing feature-level MELD tables would make the project safer but much less interesting. |

## Strongest story

The strongest honest story is not "we improve multimodal fusion." It is:
multimodal AI systems increasingly receive text, audio, and video, but current
evaluation mostly rewards final answers under clean or simply missing inputs.
AutoFusion-Bench asks a harder and more useful question: when evidence quality
changes at the sample level, can the model diagnose which modality is damaged,
locate the damage, decide whether another modality can recover the information,
route to a sufficient low-cost modality subset, and abstain when the evidence is
unrecoverable? This is a benchmark for evidence governance in multimodal
reasoning, not merely robustness to missing inputs.

## Better reframes

- Reframe: Instead of "build a missing-modality benchmark," study "whether
  MLLMs can govern unreliable multimodal evidence" through a controlled
  text/audio/video defect benchmark.
  Next action: Create 30 examples with explicit defect metadata and ask 2-3
  MLLMs the five diagnostic questions.
- Reframe: Instead of "use public affective datasets and add noise," study "the
  boundary between recoverable and unrecoverable evidence" through paired cases
  where one modality is broken and another either does or does not contain the
  missing cue.
  Next action: Hand-label 20 recoverable and 20 unrecoverable cases before
  writing a large annotation guideline.
- Reframe: Instead of "prove AutoFusion works on MELD," study "when a model
  should spend compute on reading, listening, or watching" through one
  affective dataset plus one non-affective audio/video reasoning dataset.
  Next action: Run a tiny pilot on both dataset families and compare whether
  failure modes are text-dominant or genuinely multimodal.

## Next action

Do a 30-50 instance pilot before committing to a large benchmark. Each instance
should include the raw modalities, controlled corruption metadata, a
recoverability label, an evidence pointer, an oracle route under one budget, and
an abstention label. The pilot succeeds only if at least one credible model
fails in an interpretable way on diagnosis, recovery, routing, or abstention;
otherwise the benchmark question is not yet sharp enough.

## Lens notes

- Hamming lens: The important problem is not "missing modalities" but
  trustworthy multimodal evidence use under real constraints. That is worth
  studying if the benchmark reaches raw modalities and evidence-level labels.
- Graham lens: The direction has the desired "simple after the fact" quality:
  models should know what evidence is broken before trusting it. The simplicity
  is a strength.
- Bourdieu lens: Do not confuse model-method papers with higher-status science.
  A rigorous benchmark can be more valuable than a marginal architecture change,
  but only if the labels and evaluation protocol are hard to dismiss.
- Vibe-coding lens: The cheap part is now implementing corruption scripts and
  generating variants. The scarce judgment is deciding which corruptions reveal
  a real failure mode rather than producing artificial cases that any model can
  detect.
