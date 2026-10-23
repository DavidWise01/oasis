from fractions import Fraction
step=3*Fraction("0.3367")-Fraction("0.0101")
uncorrected=3*Fraction("0.3367")
assert step==1
for n in [1,2,3,10,25,50,99,100,1000,100000]:
    corrected=(n*step)%1
    raw=(n*uncorrected)%1
    assert corrected==0
    print(f"{n:>6} cycles: corrected={float(corrected):.4f}, uncorrected={float(raw):.4f}, raw_unwrapped_drift={float(n*(uncorrected-1)):.4f}")
print("PASS: exact rational phase closure at tested depths")
