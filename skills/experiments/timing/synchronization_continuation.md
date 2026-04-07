# Synchronization–continuation tapping

## What it tests
Whether internal timing relies on a periodic forcing signal or on an
autonomous oscillator. The continuation phase exposes the intrinsic timing
mechanism after the external metronome stops.

## Stimuli and structure
Two phases per trial. Synchronization: ~30 isochronous tones at a target IOI
(e.g. 500 ms); participant taps with each tone. Continuation: tones stop, the
participant continues tapping for ~30 more taps at the same rate.

## Recording modality
Behavioural (tap times). Optional EEG/MEG for neural correlates.

## Key dependent measures
- `compute_rt_distribution_stats` over inter-tap intervals (continuation phase)
- `compute_learning_trajectory` of asynchrony (sync phase)
- `compute_phase_locking_value` between EEG band power and tap times if EEG is recorded

## Standard contrasts
- Inter-tap-interval mean and CV in synchronization vs. continuation phase
- Asynchrony drift sign across the synchronization phase
- Differential effect of metronome perturbations (one tone shifted) on the
  next 1–3 taps

## Variants and extensions
- Phase- vs. period-perturbation conditions
- Auditory vs. visual metronome
- Tempo limits (very fast / very slow IOIs)

## Constraints and confounds
- Hardware tap latency must be characterised; software MIDI is unreliable
  below ~10 ms resolution.
- Drift in the continuation phase is the central measure; trials with too few
  continuation taps must be excluded.

## Lab feasibility notes
Equipment requirements are minimal: a contact pad and a precise timer.
Behavioural-only setups are feasible in a single session.

## References
Stevens (1886); Wing & Kristofferson (1973); Repp (2005).
