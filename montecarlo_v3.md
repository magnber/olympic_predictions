# Monte Carlo Simulation - V3 Methodology

## Research Summary

Based on academic research on Monte Carlo simulation for sports prediction, particularly:
- "Misadventures in Monte Carlo" (Journal of Sports Analytics, 2019)
- FiveThirtyEight World Cup/NHL prediction methodology
- Plackett-Luce model for ranking data

## Key Findings

### 1. Monte Carlo is a "Garbage-In-Garbage-Out" Estimator

> "Highly confident estimates from the Monte Carlo procedure can be mistaken for accuracy in the underlying probabilities themselves."

Running more simulations gives confidence in the **model's properties**, not in the model's correctness. A flawed model will converge to flawed results with perfect precision.

### 2. Error Correlation Must Be Accounted For

The biggest mistake in sports Monte Carlo simulation is ignoring **error correlation** across events. If we estimate athlete strength with some error, that error affects ALL competitions that athlete participates in.

**Without variance propagation**: Each simulation uses the same fixed athlete strengths, leading to:
- Overconfident predictions (probabilities too close to 0% or 100%)
- Poor calibration (predicted probabilities don't match actual outcomes)

**With variance propagation**: Each simulation samples athlete strength from a distribution:
- More realistic uncertainty
- Better calibrated probabilities
- Proper confidence intervals

### 3. Stability Comes from the Law of Large Numbers

The mean (expected value) converges as simulations increase:

```
P(|X̄ - μ| ≥ ε) ≤ σ²/(n·ε²)
```

With 100,000 simulations:
- The mean is stable regardless of random seed
- Different runs will produce nearly identical means (within ~0.1)
- This is TRUE stability through statistics, not artificial determinism from fixed seeds

### 4. The Plackett-Luce Model for Rankings

For multi-competitor events (like Olympic races), the proper statistical model is **Plackett-Luce**:

```
P(ranking) = ∏(αⱼ / Σαᵢ)
```

Where:
- αⱼ = "worth parameter" (strength) of competitor j
- Sum is over remaining competitors at each position

This is equivalent to the **rank-ordered logit model** with Gumbel noise, which we use in V1.

### 5. Output Should Be the Mean

The **expected value (mean)** is the optimal point estimate:
- Minimizes expected squared error
- Stable across runs
- Represents the "average" outcome across many possible Olympics

Round to integers for the final submission.

## V3 Model Implementation

### Changes from V1/V2

1. **Variance Propagation**: Each simulation applies random perturbation to athlete strengths
   - Models uncertainty in our strength estimates
   - Creates correlated errors within each simulation (same athlete affected across events)

2. **No Fixed Random Seed**: Stability comes from mean convergence, not determinism

3. **Strength Uncertainty Model**:
   ```python
   # For each simulation, perturb athlete strengths
   strength_multiplier = exp(N(0, σ²))  # Log-normal perturbation
   effective_strength = base_strength * strength_multiplier
   ```

4. **Plackett-Luce Simulation**:
   ```python
   # Sample performance = log(strength) + Gumbel(0, β)
   performance = log(effective_strength) + gumbel_noise()
   # Rank by performance
   ```

### Parameters

- `NUM_SIMULATIONS = 100000` (sufficient for convergence)
- `STRENGTH_UNCERTAINTY = 0.15` (15% coefficient of variation in strength estimates)
- `PERFORMANCE_VARIANCE = 1.0` (Gumbel scale for day-to-day variation)

### Validation

Run twice without fixed seed. If implementation is correct:
- Mean values should differ by < 0.1 medals per country
- Rounded predictions should be identical
- This demonstrates TRUE statistical stability

## Expected Outcomes

With proper variance propagation:
1. **Wider confidence intervals** - more honest about uncertainty
2. **Better calibration** - predicted probabilities match actual outcomes
3. **Stable means** - consistent across runs
4. **Realistic G/S/B distribution** - natural variance in medal types

## References

1. "Misadventures in Monte Carlo" - Journal of Sports Analytics, 2019
2. FiveThirtyEight: "How Our World Cup Predictions Work"
3. Plackett-Luce model (1975) for ranking data
4. "Expected Goals and the Monte Carlo Trap" - DTAI Sports Blog
