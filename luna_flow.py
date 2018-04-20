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

def accumulate(state, x,y,z, collect=1.0):
    """Recursively collect oil"""
    if collect < 0.1:
        return 0

    props = state.state.props

    gidx = state.grid.getGlobalIndex(x, y, z)

    permx = lundarcy(props['PERMX'][gidx])

    oip = _soil(state.state.table, x, y, z) * props['PORV'][gidx]

    oip += accumulate(state, x+1, y, z, collect=collect*permx)
    oip += accumulate(state, x-1, y, z, collect=collect*permx)

    return oip

def props():
    pass

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
        for comp in well:
            oip += accumulate(state, *comp.pos)

    #mockedval = len(pros)**2 * len(injs) * days  # yup

    log(state, 'idx {} pros {} injs {} -> {}'.format(step_idx,
                                                     pros,
                                                     injs,
                                                     oip))

    return oip
