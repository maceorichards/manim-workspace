# Science — "From sinusoids to spectra to impedance"

Sources: deck spec, top matter and slide 1 (takeaway, content, Say, If asked). Read 2026-09-30.

## The talk around it

- Paper: Prescott, Ratté, De Koninck & Sejnowski (2008), *Pyramidal neurons switch from
  integrators in vitro to resonators under in vivo-like conditions*, J Neurophysiol 100.
- Audience: everyone has skimmed the paper. Nobody is assumed to know Fourier transforms,
  complex numbers, power spectra or impedance. Build every idea geometrically first.
- This video opens the talk's toolkit. Slides 1–3 build the tools (frequency domain → current
  balance → decay vs ring). Slides 4–5 show real CA1 cells switching class. Slide 6 names the
  current responsible.
- The talk's refrain (introduced on slide 2, not in this video): *Whether a neuron is an
  integrator or a resonator is decided by the sign of the net current near threshold — and that
  sign is set by the synaptic background, not by the cell.*

## Slide takeaway

A signal is a sum of rotations e^{i2πft}. The **power spectrum** says how much of each rotation
is present. **Convolution** in time becomes multiplication in frequency, and that is what makes
impedance, and therefore resonance, measurable.

## Concepts, in plain words

1. **Fourier:** any signal can be rebuilt as a sum of sinusoids, x(t) = Σ_f X(f) e^{i2πft}.
   This is the same signal, written as "how much of each frequency", with nothing added or lost.
2. **Why complex numbers:** each frequency needs two numbers, a size and a timing offset (the
   phase). Write each component as a cos(2πft) + b sin(2πft) and store it as X(f) = a + ib.
   - a is the cosine part and b the sine part. |X| is the size and arg X the phase.
   - Euler's formula e^{iθ} = cos θ + i sin θ is what lets one number hold both parts.
   - Shifting a component in time moves weight between Re and Im but leaves |X| unchanged. That
     is the point of Beat A's phase slide.
3. **Power spectrum:** P(f) = |X(f)|² keeps the size and throws away the phase. A peak at f
   means the signal contains a rhythm at f. This is the y-axis of the paper's Figs 6–9.
4. **Convolution:** the membrane voltage is every past input, weighted by how much the membrane
   still "remembers" it: V(t) = (h ∗ I)(t) = ∫ h(τ) I(t − τ) dτ. This integral is spoken only,
   never shown on screen.
   - The convolution theorem turns this into multiplication: **V(f) = Z(f)·I(f)**. Here Z(f), the
     Fourier transform of h, is the **impedance** (MΩ).
   - A passive membrane has |Z| largest at 0 Hz (low-pass). **Resonance** means |Z| peaks at a
     *nonzero* frequency.
   - The paper probes Z in two ways. Sine waves test one frequency at a time (Figs 6C, 7C). Noise
     tests all frequencies at once, because output spectrum = |Z|² × input spectrum (Fig 7D).
     Beat C is that second method.
5. **Link forward, spoken:** a neuron returning to rest after a small kick behaves like e^{λt},
   with λ = σ + iω. The real part sets the decay, the imaginary part the rotation. This pays off
   in `eigenvalues_integrator_vs_resonator`. That is why this video avoids rotating phasors: the rotating point in a
   complex plane is saved for then.

The slide itself carries four equations: the Fourier sum, Euler's formula, P = |X|² and
V(f) = Z(f)·I(f). The video shows only the last one, inside a caption.

## Speaker line (Say)

"Three words for the rest of the talk: spectrum means which rhythms are present; impedance means
which rhythms the membrane amplifies; and the complex plane is just bookkeeping for size plus
timing. Hold on to 'decay and rotation' — it comes back on slide 3."

## Likely questions (why the video is built this way)

- *Sign convention:* numerical FFTs (with an e^{−iωt} kernel) return X ∝ a − ib. The a + ib
  convention is for readability; only the Im sign differs. Hence the on-screen footnote, and the
  rule that the stems are drawn from (a, b), not from an FFT.
- *Why square?* Power (amplitude²) is the convention, and it discards phase. Impedance is complex
  (magnitude and phase), and the paper plots its magnitude.
- *Frequency resolution* is set by recording length: a T-second window resolves ~1/T Hz. This is
  why Beat B's 2-s window gives 1-Hz bins, and why its peaks lag their onset.
- Primer: Hutcheon & Yarom (2000), *Trends Neurosci* 23: 216–222.
- The impedance used in Beat C is a schematic membrane: an RC membrane (τ = 20 ms) plus a slow
  opposing current (τ_w = 80 ms). That combination gives a θ-range peak near 5 Hz, like the
  4–6 Hz noise-driven peak the paper reports for shunted CA1 cells (Fig 7D, n = 3).
