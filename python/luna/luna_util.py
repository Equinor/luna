from datetime import datetime as dt

from collections import namedtuple


lunastate = namedtuple('lunastate',
                       'eclbase schedule completions grid keys state soil porv perm gidx nx ny nz')


def lunadarcy(perm):
    """Return q in [0,1) where 1 means perfect flow, 0 no flow"""
    ZERO = 10**-16
    ONE = 2000 * ZERO
    if perm >= ONE:
        return 0.999
    if perm <= ZERO:
        return 0
    return (perm - ZERO) / ONE


def log(state, msg):
    out = '{}\t{}\n'.format(dt.now(), msg)
    #with open(state.eclbase + '.PRT', 'a') as logf:
    #    logf.write(out)
    return out
