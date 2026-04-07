# Stuart–Landau

## When to use
When the theory implies the system sits near a Hopf bifurcation and amplitude
fluctuations matter as well as phase. Useful for modelling alpha generators,
cortical resonators, and any system where amplitude–phase coupling is
expected.

## Mathematical form
$$\dot z_i = (\mu + i\omega_i) z_i - |z_i|^2 z_i + \frac{K}{N}\sum_{j=1}^{N}(z_j - z_i)$$

## Primary state variables
- `z_i` — complex amplitude of oscillator *i*; the real and imaginary parts
  evolve jointly. The phase is `arg(z_i)` and the amplitude is `|z_i|`.

## Structural parameters
- `K` — diffusive coupling strength, prior range [0, 2]
- `mu` — bifurcation parameter, prior range [-0.5, 1.5]
- `omega` — natural angular frequencies, prior range [-2, 2] rad/s

## Linking functions
- `plv_from_oscillator_states` — phase-locking on `arg(z_i)`

## Compatible primitives
- `primitives.oscillators.stuart_landau`

## Characteristic falsification signatures
- `compute_psd_peak` shows a single dominant frequency for `mu > 0`
- `compute_phase_locking_value` between two oscillators increases monotonically
  with K above the bifurcation

## Known pitfalls
- For `mu < 0` the system collapses to the origin; phase becomes meaningless.
- Diffusive coupling (`z_j - z_i`) is *not* the same as Kuramoto's sinusoidal
  coupling and yields different critical behaviour.

## References
Kuramoto (1984); Pikovsky, Rosenblum & Kurths (2001).
