"""Maya + Babylon rounded clock benchmark v02: preserve Haab, add Gregorian leap clock.
Run: python3 benchmarks/aeon_maya_clock_v02.py
Rounded planetary synodic counts are NOT historical dated observations.
"""
from datetime import date
from math import lcm

P={"Tzolkin":260,"Haab":365,"Venus":584,"Mercury":116,"Mars":780,"Jupiter":399,"Saturn":378}
def leap(y):
    return y%4==0 and (y%100!=0 or y%400==0)
def span(y,years=8):
    return (date(y+years,1,1)-date(y,1,1)).days
def main():
    checks={
        "tzolkin":13*20==260,
        "haab":18*20+5==365,
        "calendar_round":lcm(260,365)==18980,
        "venus_haab_eight_year":5*584==8*365==2920,
        "venus_maya_triple":lcm(260,365,584)==37960,
        "venus_phases":236+90+250+8==584,
        "mercury_venus_lcm":lcm(116,584)==16936,
        "mercury_venus_rounding":25*116==2900 and 5*584==2920,
        "mars_venus_lcm":lcm(780,584)==113880,
        "symbolic_729":3**6==729,
        "cipher_208":208==8*26,
        "gregorian_2000":leap(2000),
        "gregorian_1900":not leap(1900),
        "gregorian_2024":leap(2024),
        "gregorian_2025":not leap(2025),
        "gregorian_400y":span(2000,400)==146097 and 146097/400==365.2425,
        "eight_year_2000":span(2000)==2922,
        "eight_year_1900":span(1900)==2921,
        "eight_year_2096":span(2096)==2921,
        "eight_year_1996":span(1996)==2922,
        "solar_vs_haab":span(2000)-8*365==2,
        "venus_haab_not_gregorian":5*584==8*365 and 5*584!=span(2000),
    }
    a,b=3,5
    for _ in range(729):a,b=b,a+b
    for _ in range(729):a,b=b-a,a
    checks["fib_roundtrip_729"]=(a,b)==(3,5)
    for year in (1900,1996,2000,2096,2024):
        print("eight-year interval",year,span(year),"drift vs 2920",span(year)-2920)
    print("day 37960 mod", {k:37960%v for k,v in P.items()})
    for label,passed in checks.items():print("PASS" if passed else "FAIL",label)
    print(sum(checks.values()),"/",len(checks))
    assert all(checks.values())
if __name__=="__main__": main()
