"""A.E.O.N. / Maya / Babylon rounded-period arithmetic regression.
Run: python3 benchmarks/aeon_maya_clock_v01.py
Dates are abstract day offsets, NOT reconstructions of dated observations.
"""
from math import lcm
P={"Tzolkin":260,"Haab":365,"Venus":584,"Mercury":116,"Mars":780,"Jupiter":399,"Saturn":378}
def main():
    checks = {
        "tzolkin":13*20==260,
        "haab":18*20+5==365,
        "calendar_round":lcm(260,365)==18980,
        "venus_8_year":5*584==8*365==2920,
        "venus_maya_triple":lcm(260,365,584)==37960,
        "dresden_venus_phases":236+90+250+8==584,
        "mercury_venus_lcm":lcm(116,584)==16936,
        "mercury_rounding_not_exact":25*116==2900 and 5*584==2920,
        "mars_venus_lcm":lcm(780,584)==113880,
        "729_symbolic":3**6==729,
        "cipher":208==8*26,
    }
    a,b=3,5
    for _ in range(729):a,b=b,a+b
    for _ in range(729):a,b=b-a,a
    checks["fib_forward_inverse"]=(a,b)==(3,5)
    for n in (18980,37960,16936,2920):
        print("day",n,{k:n%v for k,v in P.items()})
    for name,ok in checks.items(): print("PASS" if ok else "FAIL",name)
    print(f"{sum(checks.values())}/{len(checks)} PASS")
    assert all(checks.values())
if __name__=="__main__":main()
