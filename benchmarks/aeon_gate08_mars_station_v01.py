"""Gate 08 — Mars stationary points in astronomical year -651 (652 BCE).
Requires pyswisseph. Geocentric Moshier ecliptic longitude speed,
Julian calendar, 12:00 UT scanning; NOT an observation-date validation.
"""
import swisseph as swe
def speed(jd):
    return swe.calc_ut(jd,swe.MARS,swe.FLG_MOSEPH|swe.FLG_SPEED)[0][3]
def bisect(a,b):
    fa=speed(a)
    assert fa*speed(b)<0
    for _ in range(55):
        m=(a+b)/2
        if fa*speed(m)<=0:b=m
        else:a=m;fa=speed(a)
    return (a+b)/2
def run():
    start=swe.julday(-651,1,1,12,swe.JUL_CAL)
    end=swe.julday(-651,12,31,12,swe.JUL_CAL)
    roots=[];jd=start
    while jd<end:
        if speed(jd)*speed(jd+1)<0:roots.append(bisect(jd,jd+1))
        jd+=1
    for jd in roots:
        print("Mars station Julian:",swe.revjul(jd,swe.JUL_CAL),
              "speed deg/day:",speed(jd))
    april=swe.julday(-651,4,8,12,swe.JUL_CAL)
    checks={
       "two station points in 652 BCE":len(roots)==2,
       "station speeds near zero":all(abs(speed(x))<3e-6 for x in roots),
       "April 8 retrograde":speed(april)<-0.2,
       "station events bracket April 8":roots[0]<april<roots[1],
       "first switch plus to minus":speed(roots[0]-1)>0 and speed(roots[0]+1)<0,
       "second switch minus to plus":speed(roots[1]-1)<0 and speed(roots[1]+1)>0,
    }
    for k,v in checks.items():print("PASS" if v else "FAIL",k)
    print("RESULT",sum(checks.values()),"/",len(checks))
    assert all(checks.values())
if __name__=="__main__":run()
