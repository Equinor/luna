from ecl.summary import EclSumVarType, EclSum

from parser import KEYS
from luna_flow import flow
from luna_util import log


# TODO
#
# Perhaps we only need F[OGW]P[RT] and should _fix_ the output to those
#
# Need to get wells, their type (injection/production) as well as report dates.


def _extract_var_list(keys, smry):
    var_list = []
    for key in keys:
        wgname = None
        num = -1
        var_type = EclSum.var_type(key)
        if var_type in (EclSumVarType.ECL_SMSPEC_WELL_VAR,
                        EclSumVarType.ECL_SMSPEC_GROUP_VAR):
            try:
                tmp = key.split(':')
                kw = tmp[0]
                wgname = tmp[1]
            except IndexError as err:
                raise ValueError('Broken key {}: {}'.format(key, err))
        elif var_type == EclSumVarType.ECL_SMSPEC_FIELD_VAR:
            kw = key
        else:
            raise ValueError(
                'Only field, well and group variables are allowed, not {}'.format(key))
        var_list.append(smry.addVariable(kw, wgname=wgname, num=num))
    return var_list





def generate_summary(state):
    sim_start = state.schedule.start
    x, y, z = state.grid.getNX(), state.grid.getNY(), state.grid.getNZ()

    ecl_sum = EclSum.restart_writer(state.eclbase, None, -1, sim_start, x, y, z)

    var_list = _extract_var_list(KEYS, ecl_sum)

    msg = 'start={}\nend={}\ntimesteps={}'.format(state.schedule.start,
                                                  state.schedule.end,
                                                  state.schedule.timesteps)
    log(state, msg)

    days = 0
    prev = None
    for idx, step in enumerate(state.schedule.timesteps):
        if prev is not None:
            days = (step - prev).days
        prev = step
        t_step = ecl_sum.add_t_step(idx, sim_days=days)

        for var in var_list:
            key = var.getKey1()
            t_step[key] = flow(state, idx, key)

        log(state, t_step)

    return ecl_sum
