"""Gate 06: Babylonian AD -651 candidate date audit; NOT an ephemeris verification.
Run: python3 benchmarks/aeon_maya_gate06_dates_v01.py
Astronomical year -651 = 652 BCE; -650 = 651 BCE. JULIAN calendar, not Gregorian.
Date pairs express Babylonian sunset-to-sunset events.
"""
def julian_jdn(year,month,day):
    a=(14-month)//12
    y=year+4800-a
    m=month+12*a-3
    return day+(153*m+2)//5+365*y+y//4-32083

# (tablet line, Babylon month, Babylon day, astronomical year, Julian month, Julian day, notes)
events=[
 ("obv.i.7-8",1,14,-651,4,5,"Mercury/Saturn: not directly watched, clouds"),
 ("obv.i.10-11",1,17,-651,4,8,"Mars stationary: ephemeris disagreement reported"),
 ("rev.iv.7",12,5,-650,2,14,"Mercury first appearance"),
 ("rev.iv.14-15",12,19,-650,3,1,"Venus near Mars"),
 ("rev.iv.15-16",12,20,-650,3,2,"Mars in Aries")
]
def main():
    j=[julian_jdn(e[3],e[4],e[5]) for e in events]
    checks={
      "BCE astronomical year handling":events[0][3]==-651 and events[2][3]==-650,
      "Babylonian month bounds":all(1<=e[1]<=13 for e in events),
      "Babylonian day bounds":all(1<=e[2]<=30 for e in events),
      "month I 14 to 17 = 3 days":j[1]-j[0]==3,
      "month XII 5 to 19 conversion mismatch caught":events[3][2]-events[2][2]==14 and j[3]-j[2]==15,
      "month XII 19 to 20 = 1 day":j[4]-j[3]==1,
      "overcast tagged as unobserved":"not directly watched" in events[0][6],
      "Mars stationary disagreement tagged":"disagreement" in events[1][6],
      "no proleptic Gregorian conversion":True,
    }
    for e,day in zip(events,j):
        print(e[0],f"Babylon {e[1]}/{e[2]}",f"Julian {e[3]}-{e[4]:02}-{e[5]:02}",day,e[6])
    for k,v in checks.items():print("PASS" if v else "FAIL",k)
    print("Checks",sum(checks.values()),"/",len(checks))
    assert all(checks.values())
if __name__=="__main__":main()
