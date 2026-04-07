# Frequency tagging

## What it tests
Whether the cortex tracks a periodic acoustic feature at a target rate (the
"tag"). Distinguishes theories that predict cortical entrainment from
theories that predict only transient evoked responses.

## Stimuli and structure
Continuous broadband sound (noise or tone carrier) amplitude-modulated at a
fixed rate (e.g. 4 Hz, 40 Hz). Trials lasting tens of seconds; multiple
modulation rates blocked across runs.

## Recording modality
EEG (auditory steady-state response paradigm) or MEG.

## Key dependent measures
- `compute_band_power` at the tagging frequency and its harmonics
- `compute_phase_locking_value` between the stimulus envelope and the EEG
- `compute_inter_trial_coherence` at the tagging frequency

## Standard contrasts
- Power at f_tag vs. neighbouring frequencies (qualitative peak presence)
- ITC at f_tag for high vs. low modulation depth (qualitative ordering)
- Topographic location of the tagged response (auditory vs. parietal sites)

## Variants and extensions
- Speech-envelope tagging (carrier is natural speech)
- Multi-frequency tagging for objective grouping experiments

## Constraints and confounds
- The tag frequency must avoid line noise and its harmonics.
- Adaptation reduces response amplitude across long blocks; counterbalance
  rates.
- For 40 Hz tagging in particular, electromyographic contamination is a
  serious confound — clip windows and check muscle artefact.

## Lab feasibility notes
Standard 64-channel EEG, intracranial-friendly, short setup. Analysis pipeline
is well-established (FieldTrip, MNE).

## References
Galambos et al. (1981); Picton et al. (2003); Lakatos et al. (2008).
