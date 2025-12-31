import numpy as np


def peralte_viga(L: float):
    return np.ceil(L / 25)


def wt_viga(Ms: float, ds: float):
    return 5 * Ms / ds
