# Mathematical consistency note for the screening operator

This note supports the manuscript section "Mathematical consistency of the
screening operator". It documents the theoretical role of the
FEM-Dijkstra-DEM workflow without changing the bounded screening claim.

## Operator view

The workflow is interpreted as a screening operator:

`S: X(t) -> Ie(t) -> P*(t) -> ADEM(t) -> MDEM -> X(t + dt)`

where `X(t) = {h, c, chi, d, K}` is the continuum state, `Ie` is the
dimensionless erosive intensity, `P*` is the Dijkstra minimum-cost
exit-to-source path, `ADEM` is the activated local DEM corridor and `MDEM` is
the homogenized DEM closure returned to the continuum cells.

## Cost and connectivity

For adjacent cells `i` and `j`, the graph cost is

`Cij(t) = lij / [epsilon + Ie,ij(t)]`, with `Ie,ij(t) >= 0` and `epsilon > 0`.

The cost is non-negative and decreases as the erosive intensity increases. The
path index is therefore a connected-corridor functional rather than a pointwise
maximum of hydraulic gradient or damage.

## Consistency requirements

- Non-negativity: `c`, `chi`, `d`, `Ie`, graph costs and DEM returned
  multipliers are clipped to admissible ranges.
- Conservation: erodible fines removed from `chi` are accounted for in the
  mobile/deposited balance or in the DEM detachment return.
- Monotonicity: for fixed weights and boundary conditions, increasing
  connected erosive intensity cannot increase the Dijkstra path cost.
- Boundedness: `K <= Kmax`, `0 <= d <= 1`, `0 <= chi <= chi0` and the DEM
  displacement subcycling limit prevent nonphysical growth.

## Interpretation of GD

`GD(t)` is a positive-safe global margin surrogate, not a degradation amount
that should increase with damage. In the benchmark, decreasing `GD(t)` means
that the global reserve is being consumed, and the reference threshold is
`GD(t) = 1`. It is not a calibrated probability of failure, collapse index or
field alarm. The benchmark asks whether the local path functional `Lambda(t)`
can identify a connected erosive corridor before the separate global
safe-margin functional `GD(t)` reaches its threshold.

## Interpretation of Lambda

`Lambda(t)` is a positive threshold ratio. It is dimensionless but not bounded
above; values larger than one mean that the connected path has crossed the
screening threshold. When a bounded display index is needed, the equivalent
monotone transform is

`Lambda_bar(t) = Lambda(t) / [1 + Lambda(t)]`, with `0 <= Lambda_bar < 1`.

The manuscript keeps `Lambda(t)` as the operational screening ratio because its
threshold is directly interpretable at `Lambda = 1`.

## Expanded symbol list for the consistency argument

- `q`: Darcy flux returned by the continuum head solve.
- `Cij`: non-negative graph cost for adjacent cells `i` and `j`.
- `P*`: Dijkstra minimum-cost exit-to-source path.
- `ADEM` or `Omega_DEM`: activated DEM corridor/window.
- `MDEM`: local DEM closure operator returning homogenized continuum updates.
- `epsilon`: positive regularization constant in the graph cost.
- `Lref`: reference path scale used to make `Lambda` dimensionless.
- `Lambda_crit`: screening threshold, equal to one in the benchmark.
- `kappa_DEM`: DEM-returned permeability multiplier.
- `eta_DEM`: DEM-returned detachment multiplier.
- `m_f,loss`: detached fine mass returned by the local DEM window.

## DEM-to-continuum closure

The DEM window is a local closure operator, not a full-dam particle simulation.
It receives local hydraulic drag, fines reserve and stress state from the
activated corridor, advances bonded particles under the subcycled displacement
bound and returns homogenized detachment and permeability multipliers.

## Algorithmic checks

The reproducibility package records:

- mass-balance residuals in the manufactured transport benchmark;
- mesh stability of the connected-path index;
- active DEM-cell fraction;
- component-ablation baselines;
- Connectivity Gain;
- DEM Closure Gain;
- DEM Activation Efficiency.

These checks support a mathematically bounded screening formulation, not
operational field validation.
