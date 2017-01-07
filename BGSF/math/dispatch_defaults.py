
def re(obj):
    return obj.real

def im(obj):
    return obj.imag

def conjugate(obj):
    try:
        return obj.conjugate()
    except AttributeError:
        pass

    try:
        r = re(obj)
        i = im(obj)
        return obj.__class__(r, i)
    except AttributeError:
        pass

    return obj


_abs = abs
abs = _abs


def abs_sq(obj):
    from .complex import Complex
    cobj = Complex(obj)
    return cobj.abs_sq()

