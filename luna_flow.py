from ecl.summary import EclSumVarType, EclSum

from luna_util import log

def flow(state, step_idx, key):
    """Takes a schedule and a step_idx and returns FOPR/FOPT for that step"""
    now = state.schedule.timesteps[step_idx]
    try:
        nxt = state.schedule.timesteps[step_idx + 1]
    except IndexError:
        nxt = state. schedule.end
    days = (nxt - now).days
    wls = [w for w in state.schedule.wells if w.status(step_idx) == u'OPEN']
    pros = [w for w in wls if w.isproducer(step_idx)]
    injs = [w for w in wls if w.isinjector(step_idx)]

    mockedval = len(pros)**2 * len(injs) * days  # yup

    log(state, 'idx {} pros {} injs {} -> {}'.format(step_idx,
                                                     pros,
                                                     injs,
                                                     mockedval))

    return mockedval
