from ecl.summary import EclSumVarType, EclSum

from luna_util import log


def lunadarcy(perm):
    """Return q in [0,1) where 1 means perfect flow, 0 no flow"""
    ZERO = 10**-12
    ONE = 2000*ZERO
    if perm >= ONE:
        return 0.999
    if perm <= ZERO:
        return 0
    return (perm - ZERO) / ONE

def _soil(table, x,y,z):
    return 1 - table['SWOF']('SW', 0.0)

def accumulate(state, x,y,z, collect=1.0, n=3):
    """Recursively collect oil"""
    if collect < 0.1 or n <= 0:
        return 0.
    if min(x,y,z) < 0:
        return 0.

    props = state.state.props()

    gidx = state.grid.globalIndex(x, y, z)

    permx = lunadarcy(props['PERMX'][gidx])
    permy = lunadarcy(props['PERMY'][gidx])
    permz = lunadarcy(props['PERMZ'][gidx])

    oip = _soil(state.state.table, x, y, z) * props['PORV'][gidx]

    oip += accumulate(state, x+1, y, z, collect=collect*permx, n=n-1)
    oip += accumulate(state, x-1, y, z, collect=collect*permx, n=n-1)

    oip += accumulate(state, x, y+1, z, collect=collect*permy, n=n-1)
    oip += accumulate(state, x, y-1, z, collect=collect*permy, n=n-1)

    oip += accumulate(state, x, y, z+1, collect=collect*permz, n=n-1)
    oip += accumulate(state, x, y, z-1, collect=collect*permz, n=n-1)

    return oip

def completions(state, step_idx):
    wls = [w for w in state.schedule.wells if w.status(step_idx) == u'OPEN']
    pros = [w for w in wls if w.isproducer(step_idx)]
    injs = [w for w in wls if w.isinjector(step_idx)]

    pcomp = [w.completions(step_idx) for w in pros]
    icomp = [w.completions(step_idx) for w in injs]
    return pcomp, icomp


def flow(state, step_idx, key):
    """Takes a schedule and a step_idx and returns FOPR/FOPT for that step"""
    now = state.schedule.timesteps[step_idx]
    try:
        nxt = state.schedule.timesteps[step_idx + 1]
    except IndexError:
        nxt = state.schedule.end
    days = (nxt - now).days

    pcomp, icomp = completions(state, step_idx)

    oip = 0
    for well in pcomp:
        if well:
            comp = well[0]
            oip += accumulate(state, *comp.pos)

    oip *= days

    #mockedval = len(pros)**2 * len(injs) * days  # yup

    log(state, 'idx {} ({} days) pros {} injs {} -> {}'.format(step_idx,
                                                               days,
                                                               pcomp,
                                                               icomp,
                                                               oip))

    return oip
