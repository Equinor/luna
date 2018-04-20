from datetime import datetime as dt

from collections import namedtuple

lunastate = namedtuple('lunastate',
                       'eclbase schedule grid keys state')

def log(state, msg):
    out = '{}\t{}\n'.format(dt.now(), msg)
    #with open(state.eclbase + '.PRT', 'a') as logf:
    #    logf.write(out)
    return out
