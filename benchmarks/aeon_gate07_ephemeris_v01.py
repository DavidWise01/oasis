"""Gate 07: Julian BCE planetary coordinates, Swiss Ephemeris Moshier backend.
Run: python3 benchmarks/aeon_gate07_ephemeris_v01.py
Dependency: pyswisseph; geocentric ecliptic longitudes. These are candidate dates,
NOT independently proven tablet chronologies or visibility determinations.
"""
import swisseph as swe
def position(y,m,d,body,hour=12):
    jd=swe.julday(y,m,d,hour,swe.JUL_CAL)
    data,flags=swe.calc_ut(jd,body,swe.FLG_MOSEPH|swe.FLG_SPEED)
    return dict(jd=jd,longitude=data[0],latitude=data[1],speed=data[3],flags=flags)
def diff(a,b): return abs((a-b+180)%360-180)
def main():
    venus=position(-650,3,1,swe.VENUS)
    mars=position(-650,3,1,swe.MARS)
    mercury=position(-650,2,14,swe.MERCURY)
    mars_april=position(-651,4,8,swe.MARS)
    checks={
      "Venus in Aries":0<=venus["longitude"]<30,
      "Mars in Aries":0<=mars["longitude"]<30,
      "Venus Mars longitude separation under 1 degree":diff(venus["longitude"],mars["longitude"])<1,
      "Venus Mars latitude separation under 1 degree":abs(venus["latitude"]-mars["latitude"])<1,
      "Mercury coordinates available":0<=mercury["longitude"]<360,
      "Moshier backend returned":bool(venus["flags"]&swe.FLG_MOSEPH),
      "Julian day sequencing":position(-650,3,2,swe.VENUS)["jd"]-venus["jd"]==1
    }
    print("651 BCE Mar 1 Julian noon:")
    print("Venus ecliptic longitude",venus["longitude"],"Mars",mars["longitude"])
    print("Longitude separation",diff(venus["longitude"],mars["longitude"]))
    print("652 BCE Apr 8 Mars longitude rate",mars_april["speed"],"deg/day")
    print("NOTE: noon separation is not a Babylonian sunset observation.")
    for name,ok in checks.items():print("PASS" if ok else "FAIL",name)
    print(sum(checks.values()),"/",len(checks))
    assert all(checks.values())
if __name__=="__main__":main()
