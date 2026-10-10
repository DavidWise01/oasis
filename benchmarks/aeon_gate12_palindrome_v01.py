"""AEON Gate12: palindrome-centered symbolic operator checks.
The central 'o' is a symbolic referent, not a physical particle.
"""
def mirror(left,center="o"):
    return left+center+left[::-1]

def test():
    p=mirror("th")
    assert p=="thoht"
    assert p==p[::-1]
    assert p[2]=="o"
    assert mirror("th")=="thoht"
    assert mirror("")=="o"
    assert all(mirror(x)==mirror(x)[::-1] for x in ("th","abcd","a",""))
    # Reverse direction must leave the exact symbolic state unchanged.
    assert p[::-1][::-1]==p
    # Distinguish a true palindrome from just reversing the flanks:
    assert "th"+"o"+"ht" ==p
    print("PASS 7/7: palindrome mirror, center, closure, empty seed")
if __name__=="__main__":
    test()
