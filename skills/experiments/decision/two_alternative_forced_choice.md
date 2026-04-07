# Two-alternative forced choice (2AFC)

## What it tests
Whether a theory's account of evidence accumulation produces the qualitative
RT and accuracy patterns expected as evidence strength varies. Distinguishes
fast-guessing accounts from accumulation accounts.

## Stimuli and structure
Brief perceptual stimuli with a continuous evidence parameter (e.g. random-dot
motion coherence, Gabor contrast). Two response keys; participants choose the
correct alternative as quickly and accurately as they can. Multiple evidence
levels interleaved across trials.

## Recording modality
Behavioural (RT, accuracy). Optional EEG for choice-locked decision signals.

## Key dependent measures
- `compute_rt_distribution_stats` per evidence level
- `compute_accuracy_curve` across evidence levels
- `compute_erp_component_amplitude` for the centro-parietal positivity, when
  EEG is collected

## Standard contrasts
- Accuracy monotonically increases with evidence level (psychometric ordering)
- Mean RT monotonically decreases with evidence level (chronometric ordering)
- RT distribution shape (right-skew) qualitatively preserved across levels

## Variants and extensions
- Speed–accuracy trade-off cued blocks
- Confidence ratings
- Rewards manipulated to bias one alternative

## Constraints and confounds
- Sequential dependencies between trials inflate apparent slope; counterbalance
  evidence sequences.
- Motor preparation contaminates RT for pre-cued responses.
- For very low coherence, lapse trials dominate; trim or model explicitly.

## Lab feasibility notes
Standard psychophysics setup. PsychoPy / Psychtoolbox templates are widely
available.

## References
Ratcliff (1978); Roitman & Shadlen (2002); Gold & Shadlen (2007).
