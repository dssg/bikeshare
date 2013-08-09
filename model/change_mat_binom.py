# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

def change_mat_binom(ts, binom, d):
    """Recieve a time series and a markov delay period.
       Return a matix of that design."""
    import numpy as np
    n=len(ts)
    x = np.array(ts[(d-1):n-1])
    for r in range(2,d+1):
        b = np.array(ts[(d-r):(n-r)])
        x = np.concatenate([x.reshape(len(x),-1),b.reshape(len(b),-1)],axis=1)
    y = binom[d:]
    return x, y
    

