##!FAIL: SlicingError[dict[alpha:beta]]@7:8

def dict_ajout(D, k, v):
    """ dict[alpha:beta] * alpha * beta -> dict[alpha:beta]"""

    # R : dict[alpha:beta]
    R = D[:]

    R[k] = v
    return R
