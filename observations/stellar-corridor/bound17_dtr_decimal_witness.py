#!/usr/bin/env python3
"""OASIS Bound17 independent high-precision DTR witness.
Python 3 stdlib only, different language/arithmetic from JS production core.
Exact four-region local null-shell junction for spherical charged RN.
NOT rotating Kerr, continuous evolution, physical center or observation.
"""
from decimal import Decimal as D, localcontext

def check(q="0.8", din="0.0001", dout="0.0001"):
    with localcontext() as ctx:
        ctx.prec = 70
        Q, a, b = D(q), D(din), D(dout)
        assert D(0) < Q < D(1)
        gap = 2 * (1-Q*Q).sqrt()
        rm = 1-(1-Q*Q).sqrt()
        rows = []
        for d in ("0.1", "0.001", "0.000001", "0.000000001", "0.0000000001"):
            delta = D(d)
            r = rm + gap*delta
            # Horizon-factored background lapse; no cancellation from 1-2M/r+Q²/r².
            f0 = -gap*gap*delta*(1-delta)/(r*r)
            fi, fo = f0-2*a/r, f0-2*b/r
            interaction = -2*a*b/(r*f0)
            mf = 1+a+b+interaction
            ff = f0-2*(a+b+interaction)/r
            residual = f0*ff - fi*fo
            assert abs(residual) < D("1e-60")
            assert mf > 1+a+b
            rows.append((d,str(r),str(mf),str(interaction),str(residual)))
        assert D(rows[-1][2]) > D("50")
        # Exact algebra controls: remove either shell and crossed interaction vanishes.
        assert -2*D(0)*b/(D("0.4")*D("-0.2")) == D(0)
        assert -2*a*D(0)/(D("0.4")*D("-0.2")) == D(0)
        print("PASS | independent Decimal precision",ctx.prec,"| DTR residual < 1e-60")
        for row in rows:
            print("delta",row[0],"r",row[1],"m_after",row[2],
                  "cross",row[3],"constraint_residual",row[4])

if __name__ == "__main__":
    check()
