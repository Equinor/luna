from ecl.summary import EclSumVarType, EclSum

# TODO
#
# Perhaps we only need F[OGW]P[RT] and should _fix_ the output to those
#
# Need to get wells, their type (injection/production) as well as report dates.


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
            t_step[key] = _mock(state, idx, key)

        log(state, t_step)

    return ecl_sum
