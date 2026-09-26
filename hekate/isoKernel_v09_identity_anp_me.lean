namespace HEKATE

/-
  isoKernel v09 — identity / ANP / ME register
  -------------------------------------------
  Append-only correction from the author:

      i :: a n p :: me :: 3 :: 6 :: 0 :: e :: 6 ::

  This file preserves the register literally.
  No semantic expansion is assigned to a, n, p, or me here.
-/

def resultRegisterV09 : List String :=
  ["i", "a", "n", "p", "me", "3", "6", "0", "e", "6"]

theorem resultRegisterV09_exact :
    resultRegisterV09 =
      ["i", "a", "n", "p", "me", "3", "6", "0", "e", "6"] := by
  rfl

theorem resultRegisterV09_length :
    resultRegisterV09.length = 10 := by
  rfl

/-
  Canonical stream:

    i :: a n p :: me :: 3 :: 6 :: 0 :: e :: 6 ::

  Existing binding retained from v08:
    e = Engineers

  Newly supplied tokens remain literal:
    i
    a
    n
    p
    me
-/

end HEKATE
