import numpy as np


def load_y(fname):
    """Load the 'y' image file.
    
    Note
    ----
    It is assumed throughout this package the 0 and '0' 
    represent baseline/jitter TRs
    """
    
    return np.loadtxt(fname, delimiter=",", dtype=np.str)


def files2onsets(files):
    """Convert a file list to a binary onsets and trial_index
    lists
    
    Note
    ----
    files presumably comes from load_y
    """
    
    findex = np.unique(
        [0 if (fi == 0) or (fi == '0') else i for i, fi in enumerate(files)]
        ) ## Such an indirect, shit, way to do this
    
    onsets = np.zeros_like(files, dtype=np.int)
    onsets[findex] = 1

    trial_index = np.empty(onsets.shape, dtype=np.float)
    trial_index[:] = np.nan
    trial_index[findex] = range(np.sum(onsets))
    
    return onsets, trial_index