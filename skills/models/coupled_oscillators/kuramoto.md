# Kuramoto

## When to use
When the theory predicts emergent phase synchrony between oscillating
populations whose coupling is well-approximated as weak and sinusoidal in the
phase difference. Canonical for entrainment, group synchrony transitions, and
cortical-tracking phenomena.

## Mathematical form
$$\dot\phi_i = \omega_i + \frac{K}{N}\sum_{j=1}^{N}\sin(\phi_j - \phi_i)$$

## Primary state variables
- `phi_i` — phase of oscillator *i* (radians, unbounded)

## Structural parameters
- `K` — global coupling strength, prior range [0, 5]
- `omega` — natural frequency distribution, prior range [-2, 2] rad/s

## Linking functions
- `plv_from_oscillator_states` — phase-locking value between two phase channels
- `rt_from_phase_threshold` — derive an RT from when a phase first crosses a threshold

## Compatible primitives
- `primitives.oscillators.kuramoto`

## Characteristic falsification signatures
- `compute_phase_locking_value` increases sharply at a critical coupling K_c
- `compute_peak_frequency` of the mean field tracks the median natural frequency

## Known pitfalls
- The all-to-all assumption hides any topological structure; adding sparse
  connectivity can change critical coupling by orders of magnitude.
- Euler integration is fine for K in the bounded range but blows up for very
  large K with large dt.

## References
Kuramoto (1984); Acebrón et al. (2005, RMP).
