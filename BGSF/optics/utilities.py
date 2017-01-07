
def kFwrapR(val, *pkpk):
    if callable(val):
        v = val(*pkpk)
    else:
        v = val
    assert(v.imag == 0)
    return v
