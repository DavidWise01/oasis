/-!
ROOT0 P2.0 — conditional 3D centered-difference scalar-wave CFL facts.
Lean 4 DRAFT, NOT COMPILED IN THIS SESSION.
This is an ancillary physical hypothesis, not a theorem about the frozen ROOT0
kernel or about external reality.
-/
import Lean
namespace ROOT0P20

/-- At the spatial Nyquist corner of a 3D cubic grid,
  the wave-dispersion right-hand side equals 3*r^2. -/
def nyquistBound (courantSquared : ℚ) : ℚ := 3 * courantSquared

/-- The simple equality a=l_P, tau=t_P gives r^2=1 and violates CFL. -/
theorem naive_planck_nyquist_exceeds_unity :
    nyquistBound 1 > 1 := by
  norm_num [nyquistBound]

/-- The minimum stable spatial pitch for a Planck time tick has r^2=1/3.
This equality is marginal at the Nyquist corner; no strict stability claimed. -/
theorem critical_planck_grid_at_boundary :
    nyquistBound (1/3 : ℚ) = 1 := by
  norm_num [nyquistBound]

/-- A strictly interior choice r=1/2 gives r^2=1/4 and strict CFL. -/
theorem interior_choice_strictly_within_bound :
    nyquistBound (1/4 : ℚ) < 1 := by
  norm_num [nyquistBound]

/-- Low-wavenumber axis group-velocity deficit coefficient for r^2=1/3. -/
theorem axis_quadratic_coefficient :
    ((1 : ℚ) - 1/3) / 8 = 1/12 := by
  norm_num

/-- At r^2=1/3, diagonal low-k leading dispersion cancels. -/
theorem body_diagonal_quadratic_coefficient :
    ((1/3 : ℚ) - 1/3) / 8 = 0 := by
  norm_num

end ROOT0P20
