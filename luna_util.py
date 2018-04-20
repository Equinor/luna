from datetime import datetime as dt


def log(state, msg):
    out = '{}\t{}\n'.format(dt.now(), msg)
    with open(state.eclbase + '.PRT', 'a') as logf:
        logf.write(out)
    return out
