# Data Plan

The benchmark should use public raw multimodal datasets as substrates, then add
a new controlled-corruption and annotation layer.

## Candidate Substrates

Preferred initial mix:

- one affective dataset with text/audio/video alignment:
  `CMU-MOSEI`, `CMU-MOSI`, `IEMOCAP`, or `MELD`;
- one non-affective audio/video or video-understanding dataset, preferably an
  AVQA-style dataset with raw audio and video.

MELD should be treated carefully. Existing `exp-001` evidence suggests MELD can
be text-dominant, so it may be better as a diagnostic dataset than as the main
positive result.

## Required Raw Fields

Each source example should ideally expose:

- text or transcript,
- audio waveform or clip,
- video or frame sequence,
- original task label,
- alignment metadata,
- license or usage constraints.

## Corruption Metadata

Every generated corruption must record:

- affected modality,
- corruption type,
- severity,
- location,
- random seed,
- generator version.

These fields are mechanical gold labels and should not depend on LLM judgment.

## Human-Verified Labels

Human verification is required for:

- recoverability,
- recovery source modality,
- evidence span or timestamp,
- oracle route,
- final answer under corruption,
- abstention label.

