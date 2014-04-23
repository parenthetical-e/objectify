import random
import numpy as np
import nibabel as nb
from copy import deepcopy

from skimage import io

from modelmodel.behave import trials
from modelmodel.noise import white
from modelmodel.hrf import double_gamma as dg
from modelmodel.bold import create_bold
from modelmodel.misc import process_prng

from fmrilearn.preprocess.data import find_good_features


def norm(X):
    """Holistic normalization between 0-1"""
    
    X = X.astype(np.float)
    return (X - X.min()) / (X.max() - X.min())
    
    
def img2nii(images, jit=(8,18), clean=True, null=False, prng=None):
    """Convert a list of images into a mock BOLD dataset (as Nifit1)."""

    prng = process_prng(prng)

    TR          = 2
    HRF_WIDTH   = 32                            ## In s
    WINDOW      = 16                            ## In TR
    HRF         = dg(width=HRF_WIDTH, TR=TR)    ## The HRF curve
    
    images = io.ImageCollection(images)
    files = images.files
    L = len(images)
    
    # Create image presentation series
    series, prng = trials.random(1,L, prng=prng)
    series, prng = trials.jitter(
            series, code=0, fraction=.99, jit=jit, prng=prng
            )
            
    try:
        x, y = images[0].shape
        images = images.concatenate().astype(np.float)
    except ValueError:
        images = images.concatenate().astype(np.float)[:,:,:,0] ## if RGB
        _, x, y = images.shape
            
    # Convert 3d image stacks (t, x, y) to 2d (time, x * y)
    # And zscore the pixels
    X = reshape2d(images)
    
    # Find feature with non-zero features, i.e. good?
    if clean:
        good = find_good_features(X, sparse=False)
    else:
        good = range(X.shape[1])
    X[:,good] = norm(X[:,good])  ## 0-1 norm
    
    if null:
        shuffledgood = deepcopy(good)        
        for i in range(X.shape[0]):
            random.shuffle(shuffledgood)
            X[i,good] = X[i,shuffledgood]
    
    # Create nifti/BOLD data
    Xbold = np.zeros([len(series), X.shape[1]])
    for j in good:
        x_jit = np.zeros_like(series, dtype=np.float)
        x_jit[series > 0] = np.squeeze(X[:,j])
        
        epsilon, prng = white(x_jit.shape[0], sigma=1.0, prng=prng)
        Xbold[:,j] = create_bold([x_jit], HRF, epsilon)

    ## transpose puts time in the last axis, 
    ## as is custom in nifti files, then swap x
    ## and y to match the incoming files
    return nb.Nifti1Image(
            np.swapaxes(undo2d(Xbold, x, y).transpose(), 0, 1), 
            np.eye(4), None
            ), [[files.pop(0) if t > 0 else '0' for t in series]], prng
    
    
def reshape2d(in3d, axis=0):
    """Treat a 3d ImageCollection as a 2d image set in time 
    i.e. (t, x, y) and reshape it into 2d, i.e. (t, x * y)"""
    
    
    # Create X
    if axis == 0:
        t, x, y = in3d.shape
    elif axis == 1:
        x, t, y = in3d.shape
    elif axis == 2:
        x, y, t = in3d.shape
    else:
        raise ValueError("axis must be (0, 1, 2)")
    X = np.zeros((t, x * y), in3d.dtype)  ## Conserve dtype
    
    # Reshape
    n_fea = 0
    for i in range(x):
        for j in range(y):
            if axis == 0:
                X[:,n_fea] = in3d[:,i,j]
            elif axis == 1:
                X[:,n_fea] = in3d[i,:,j]
            elif axis == 2:
                X[:,n_fea] = in3d[i,j,:]
            else:
                raise ValueError("axis must be (0, 1, 2)")
            n_fea +=1
    
    return X


def undo2d(X, x, y, axis=0):
    """Undoes reshape2d(), returning a np.array"""
    
    t = X.shape[axis]
    
    # Create X in3d
    if axis == 0:
        in3d = np.zeros((t, x, y), dtype=X.dtype)
    elif axis == 1:
        in3d = np.zeros((x, t, y), dtype=X.dtype) ## Conserve dtype
    elif axis == 2:
        in3d = np.zeros((x, y, t), dtype=X.dtype) ## Conserve dtype
    else:
        raise ValueError("axis must be (0, 1, 2)")
    
    # Reshape
    n_fea = 0
    for i in range(x):
        for j in range(y):
            if axis == 0:
                in3d[:,i,j] = X[:,n_fea]
            elif axis == 1:
                in3d[i,:,j] = X[:,n_fea]
            elif axis == 2:           
                in3d[i,j,:] = X[:,n_fea]
            else:
                raise ValueError("axis must be (0, 1, 2)")
            n_fea += 1
    
    return in3d


def trial_space(x, onsets, window):
    """Convert a 1d array into a 2d array (n_onsets, window)."""
    
    X = np.zeros([np.sum(onsets), window])
    ocnt = 0
    for i, o in enumerate(onsets):
        if o == 1:
            X[ocnt,:] = x[range(i, i + window)]
            ocnt += 1

    assert ocnt == int(np.sum(onsets)), "Onsets and count is off"
        
    return X
    