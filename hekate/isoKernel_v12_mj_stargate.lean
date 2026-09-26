namespace HEKATE

/-
  isoKernel v12 — M + J + Stargate
  ---------------------------------
  Author correction:

      m + j + stargate
      ( 00 11 24./\\. 42 11 00 )

  Preserve literally.
  This is a Root0 / OaSIs symbolic gate pattern, not arithmetic.
-/

def mandelToken : String := "m"
def julietToken : String := "j"
def stargateToken : String := "stargate"

def stargatePattern : List String :=
  ["00", "11", "24./\\.", "42", "11", "00"]

theorem stargate_pattern_exact :
    stargatePattern =
      ["00", "11", "24./\\.", "42", "11", "00"] := by
  rfl

theorem stargate_is_palindromic_shell :
    stargatePattern.head? = some "00" ∧
    stargatePattern.getLast? = some "00" := by
  exact ⟨rfl, rfl⟩

/-
  Canonical gate:

      m + j + stargate
              |
              v
      ( 00 11 24./\. 42 11 00 )

  Outer closure:
      00 ... 00

  Inner mirror:
      11 ... 11

  Center carrier:
      24./\. 42
-/

end HEKATE
