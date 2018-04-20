from ecl.summary import EclSumVarType, EclSum

from .luna_util import log

RESERVOIR = {}




def _soil(table, x, y, z):
    return 1 - table['SWOF']('SW', 0.0)


def accumulate(state, x, y, z, collect=1.0, n=3, visited=None):
    """Recursively collect oil"""
    if collect < 0.1 or n <= 0:
        return 0.
    if min(x, y, z) < 0 or x >= state.grid.getNX() or y >= state.grid.getNY() or z >= state.grid.getNZ():
        return 0.
    gidx = state.grid.globalIndex(x, y, z)
    if gidx in RESERVOIR:
        return RESERVOIR[gidx]

    if visited is None:
        visited = set()

    if gidx in visited:
        return 0.

    visited.add(gidx)

    props = state.state.props()

    oip = _soil(state.state.table, x, y, z) * props['PORV'][gidx]

    oip += accumulate(
        state, x + 1, y, z, collect=collect * state.perm[0][gidx], n=n-1, visited=visited)
    oip += accumulate(
        state, x - 1, y, z, collect=collect * state.perm[0][gidx], n=n-1, visited=visited)

    oip += accumulate(
        state, x, y + 1, z, collect=collect * state.perm[1][gidx], n=n-1, visited=visited)
    oip += accumulate(
        state, x, y - 1, z, collect=collect * state.perm[1][gidx], n=n-1, visited=visited)

    oip += accumulate(
        state, x, y, z + 1, collect=collect * state.perm[2][gidx], n=n-1, visited=visited)
    oip += accumulate(
        state, x, y, z - 1, collect=collect * state.perm[2][gidx], n=n-1, visited=visited)

    RESERVOIR[gidx] = oip
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
    print(step_idx)
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

    oip *= days

    #mockedval = len(pros)**2 * len(injs) * days  # yup

    log(state, 'idx {} ({} days) pros {} injs {} -> {}'.format(
        step_idx, days, pcomp, icomp, oip))

    return oip
