# Science — "Two clocks, and sliding the threshold"

Sources: deck spec, top matter and slides 3, 5, 6, 7 (takeaways, content, Say, If asked);
paper, Fig 8 and Fig 9 legends. Read 2026-09-30.

## The talk around it

- Paper: Prescott et al. (2008), *Pyramidal neurons switch from integrators in vitro to
  resonators under in vivo-like conditions*, J Neurophysiol 100.
- By this point the audience has seen the following:
  - class 1 vs class 2 and the I–V hump (`iv_curve_assembled_unbent`)
  - decay vs ring, the phase plane, focus = ring, and the pulse-pair test (`eigenvalues_integrator_vs_resonator`)
  - evidence that real CA1 cells switch under dynamic-clamp shunting and tonic depolarization:
    V* up, f_min up, θ ringing (slides 4–5)
- **The refrain** (repeated verbatim on this slide): *Whether a neuron is an integrator or a
  resonator is decided by the sign of the net current near threshold — and that sign is set by
  the synaptic background, not by the cell.*

## Slide takeaway

θ ringing needs a *slow* outward current. I_K,dr is too fast; **I_M** (τ ≈ 400 ms) has the right
timing. Shunting and slow Na⁺ inactivation push threshold up the steep flank of I_M's activation
curve, which recruits it. In a quiet slice this barely happens.

## The argument, step by step

1. **The problem.** The slide 3 model rings at ~70–100 Hz, but the cells ring at θ (3–10 Hz).
   Something in the model is too fast.
2. **The fix that failed** (Fig 8A). Slowing I_K,dr (φ_w 0.25 → 0.008) brings the ringing down to
   ~10 Hz, but spikes become unphysiologically wide. A third, slower timescale is needed.
3. **The fix that works** (Fig 8B). Tune I_M to τ_z = 400 ms. Adaptation now gives ~8-Hz ringing,
   while the shunt alone still gives ~70 Hz. (Our A1, the shunted θ-model, rings at 115 Hz; the
   paper's shunted case is ~70 Hz.)
4. **Who lags whom** (Fig 8C). **This is Beat A.**
   - In fast ringing, g_K,dr lags V and g_M stays flat.
   - In θ ringing, g_K,dr keeps up with V instantly, so it can't supply the *delayed* outward
     current. **g_M lags**, so I_M does that job.
5. **Same geometry, different plane** (Fig 8D). On the V–w plane the fixed point is still a
   saddle-node (no fast ringing), but on the **V–z plane it is a focus**. This is slide 3's
   spiral with z in place of w, and slower because τ_z is long.
6. **The amplifier was right; the current was wrong** (Fig 2B | Fig 9A).
   - Extra outward current forces Na⁺ to work harder, so V* shifts up.
   - V* sits on the steep flank of the K⁺ activation curves, so a few mV recruits much more
     outward current, which shifts V* further: a self-reinforcing loop.
   - The authors first credited I_K,dr. The same loop acting on **I_M**, which is already active
     below threshold, is what matters.
7. **What shifts V\*. This is Beat B.**
   - Shunting.
   - Slow Na⁺-channel inactivation from sustained depolarization. Spike amplitude declines over
     seconds in the recordings; in the model, 33% inactivation gives a ~15% amplitude drop.
   - Either one produces θ ringing, and **removing I_M abolishes it** (Fig 9). The V–z
     intersection turns from saddle-node to focus, and the steady-state I–V becomes monotonic.
8. **Two data puzzles this explains.**
   - Unshunted cells fire slowly at step onset, because I_M isn't recruited yet.
   - They ring only after sustained depolarization, once slow inactivation has shifted V* and
     recruited I_M.
9. **Why it is state-dependent.** Shunting and cumulative Na⁺ inactivation are prominent in vivo
   and modest in vitro. Acetylcholine blocks I_M, which should push cells back toward class 1
   (Stiefel et al. 2008).

## Honesty notes the video respects

- The paper's Fig 9 uses green for "I_M removed". This deck reserves green for I_M, so that
  condition is grey here.
- The conductance traces are normalised (as in Fig 8C). The small amplitude tags show that A1's
  g_M really is nearly constant (0.1%).
- "Removing I_M abolishes θ" is a *model* result: there was no XE991 or linopirdine experiment.
  τ_z was tuned to produce θ. Both points are raised on the discussion slide.
- The noise and holding levels were tuned so no trace spikes (recorded in `model.md`). The
  qualitative result (θ peak with inactivation or shunt, none for control or without I_M) is the
  paper's.

## Speaker line (Say)

The refrain, then the self-correction: "They say it outright: they first blamed I_K,dr, and the
timing ruled it out. The amplifier idea survived — it just acts on a slower current."

## Likely questions

- *Two ways I_M can matter.* It can compete directly with I_Na, which gives θ MPOs. It can also
  supply a sustained outward current that shifts threshold and changes the I_Na–I_K,dr
  competition, which gives faster MPOs. The data (θ peaks only; f_min 10–30 spike/s) point to the
  first. This is also why the shunt variant uses g_shunt 3.5, not 4.0: at 4.0 the model's focus
  is the fast ~36-Hz mode.
- *Why is the V–z plane a fair 2-D picture?* During slow oscillations, I_K,dr follows V
  essentially instantly and acts as an instantaneously varying offset, so the competition reduces
  to slow I_Na vs ultraslow I_M.
- *Dynamic inactivation* (Fig 9 legend): ḡ_Na × h, with dh/dt = (h∞(V) − h)/τ_h,
  h∞ = 1 − 0.67/(1 + e^{(−40 − V)/8}) and τ_h = 1 s. The video uses the steady-state shortcut
  instead (a 33% cut in ḡ_Na), as the paper does for its spectra.
