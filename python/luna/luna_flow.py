from ecl.summary import EclSumVarType, EclSum

from .luna_util import log

RESERVOIR = {}


def accumulate(state, x, y, z, collect=1.0, n=3, visited=None):
    """Recursively collect oil"""
    if collect < 0.1 or n <= 0:
        return 0.
    if min(x, y, z) < 0 or x >= state.nx or y >= state.ny or z >= state.nz:
        return 0.
    gidx = state.gidx[(x, y, z)]
    if gidx in RESERVOIR:
        return RESERVOIR[gidx]

    if visited is None:
        visited = set()

    if gidx in visited:
        return 0.

    visited.add(gidx)

    #print('computing %d' % gidx)
    oip = state.soil[(x, y, z)] * state.porv[gidx]

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




def flow(state, step_idx, key):
    """Takes a schedule and a step_idx and returns FOPR/FOPT for that step"""
    #print(step_idx)

    pcomp, icomp = state.completions[step_idx]

    oip = 0
    for well in pcomp:
        for comp in well:
            oip += accumulate(state, *comp)
    days = state.days[step_idx]
    oip *= days

    #mockedval = len(pros)**2 * len(injs) * days  # yup

    log(state, 'idx {} ({} days) pros {} injs {} -> {}'.format(
        step_idx, days, pcomp, icomp, oip))

    return oip
