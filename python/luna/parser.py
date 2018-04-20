import numpy as np
import sunbeam
from .luna_util import lunastate, lunadarcy

SUNBEAM_ERRORS = ('PARSE_UNKNOWN_KEYWORD', 'PARSE_RANDOM_TEXT',
                  'PARSE_RANDOM_SLASH', 'PARSE_MISSING_DIMS_KEYWORD',
                  'PARSE_EXTRA_DATA', 'PARSE_MISSING_INCLUDE',
                  'UNSUPPORTED_SCHEDULE_GEO_MODIFIER',
                  'UNSUPPORTED_COMPORD_TYPE', 'UNSUPPORTED_INITIAL_THPRES',
                  'UNSUPPORTED_TERMINATE_IF_BHP',
                  'INTERNAL_ERROR_UNINITIALIZED_THPRES',
                  'SUMMARY_UNKNOWN_WELL', 'SUMMARY_UNKNOWN_GROUP')
SUNBEAM_ACTION = sunbeam.action.warn

_KEYS = ('FOPR',
        'FGPR',
        'FWPR',
        'FLPR',
        'FVPR',
        'FGSR',
        'FOPP',
        'FWPP',
        'FGPP',
        'FVIR',
        'FWIR',
        'FGIR',
        'FVPT',
        'FOPT',
        'FWPT',
        'FGPT',
        'FWIT',
        'FGIT',
        'FWIP',
        'FOIP',
        'FGIP',
        'FWCT',
        'FGOR',
        'FGLR',
        'FWGR',
        'FPR',
)  # TODO read from SCHEDULE


def completions(schedule, step_idx):
    wls = [w for w in schedule.wells if w.status(step_idx) == u'OPEN']
    pros = [w for w in wls if w.isproducer(step_idx)]
    injs = [w for w in wls if w.isinjector(step_idx)]

    pcomp = [[c.pos for c in w.completions(step_idx)] for w in pros]
    icomp = [[c.pos for c in w.completions(step_idx)] for w in injs]
    return pcomp, icomp


def _soil(table, x, y, z):
    return 1 - table['SWOF']('SW', 0.0)

def parse(eclbase):
    es = sunbeam.parse(eclbase + '.DATA',
                       [(err, SUNBEAM_ACTION) for err in SUNBEAM_ERRORS])
    sch = es.schedule
    grid = es.state.grid()

    props = es.state.props()
    nglob = grid.getNX() * grid.getNY() * grid.getNZ()
    print('compute %d permx ...' % nglob)
    px = props['PERMX']
    permx = np.array([lunadarcy(px[i]) for i in range(nglob)])

    print('compute %d permy ...' % nglob)
    py = props['PERMY']
    permy = np.array([lunadarcy(py[i]) for i in range(nglob)])

    print('compute %d permz ...' % nglob)
    pz = props['PERMZ']
    permz = np.array([lunadarcy(pz[i]) for i in range(nglob)])

    print('compute %d porv ...' % nglob)
    prv = props['PORV']
    porv = np.array([prv[i] for i in range(nglob)])


    nx, ny, nz = grid.getNX(), grid.getNY(), grid.getNZ()

    gidx = {}
    soil = {}
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                gidx[(i, j, k)] = grid.globalIndex(i, j, k)
                soil[(i, j, k)] = _soil(es.state.table, i, j, k)

    comps = [completions(sch, i) for i in range(len(sch.timesteps))]

    state = lunastate(eclbase=eclbase,
                      schedule=sch,
                      completions=comps,
                      grid=grid,
                      keys=[k for k in _KEYS if k in es.summary_config],
                      state=es.state,
                      soil=soil,
                      porv=porv,
                      perm=(permx, permy, permz),
                      gidx=gidx,
                      nx=nx,
                      ny=ny,
                      nz=nz,
    )
    return state
