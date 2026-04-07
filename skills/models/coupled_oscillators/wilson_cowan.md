# Wilson–Cowan

## When to use
When the theory talks about competition between excitatory and inhibitory
populations and predicts emergent oscillations in a band determined by the
E/I time constants. Standard substrate for cortical-column models.

## Mathematical form
$$\tau_E\dot E = -E + S(c_{EE} E - c_{EI} I + P)$$
$$\tau_I\dot I = -I + S(c_{IE} E - c_{II} I + Q)$$

with $S(x) = 1/(1 + e^{-a(x - \theta)})$.

## Primary state variables
- `E` — mean firing rate of the excitatory population, in [0, 1]
- `I` — mean firing rate of the inhibitory population, in [0, 1]

## Structural parameters
- `c_EE` — recurrent excitation, prior range [8, 24]
- `c_EI` — inhibition onto E, prior range [4, 20]
- `tau_E` — E-population time constant (s), prior range [0.005, 0.020]
- `tau_I` — I-population time constant (s), prior range [0.010, 0.040]
- `P` — external drive to E, prior range [0, 5]

## Linking functions
- `rt_from_phase_threshold` — applied to the Hilbert phase of the band-limited E(t)

## Compatible primitives
- `primitives.oscillators.wilson_cowan`

## Characteristic falsification signatures
- `compute_band_power` in the gamma band increases with `c_EE` once oscillations
  emerge
- `compute_peak_frequency` of E(t) sits inside the band predicted from the
  E/I time constants

## Known pitfalls
- The model has multiple stable regimes (silent, sustained, oscillatory).
  Parameter sweeps must straddle these regimes to be informative.
- Sigmoid saturation makes naive linearisations misleading near the upper
  fixed point.

## References
Wilson & Cowan (1972); Destexhe & Sejnowski (2009).
