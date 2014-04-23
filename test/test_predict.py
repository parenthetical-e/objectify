import os, shutil, glob, subprocess, argparse

import numpy as np
import nibabel as nb

import matplotlib.pyplot as plt

from skimage import io
from skimage import filter as filt

from objectify import transform


def test_data(run=True):
    """Makes fake data for testing."""
    
    shutil.rmtree('imgs', ignore_errors=True)
    shutil.rmtree('normimgs', ignore_errors=True)    
    shutil.rmtree('results', ignore_errors=True)
    shutil.rmtree('analysis', ignore_errors=True)
    shutil.rmtree('nii', ignore_errors=True)    
    os.mkdir('imgs')
    os.mkdir('normimgs')    
    os.mkdir('results')
    os.mkdir('analysis')
    os.mkdir('nii')
    
    prng = np.random.RandomState(42)
    
    x = 400
    y = 400
    t = 100
    w = 2.
    noocc = prng.rand(x,y,t)
    sd = noocc.std()
    noocc[:,180:240] *= (w * sd)
    
    occ = noocc.copy()
    occ[140:280,180:240] /= (w * sd)  ## Occlude!
    
    # Save images.
    for i in range(t):
        plt.imsave('imgs/'+str(i)+'_occ.jpg', occ[:,:,i], cmap=plt.cm.gray)
        plt.imsave('imgs/'+str(i)+'_noocc.jpg', noocc[:,:,i], cmap=plt.cm.gray)
    
    # Save norm for ref
    occn = transform.norm(occ)
    nooccn = transform.norm(noocc)
    for i in range(t):
        plt.imsave('normimgs/'+str(i)+'_occ.jpg', occn[:,:,i], cmap=plt.cm.gray)
        plt.imsave('normimgs/'+str(i)+'_noocc.jpg', nooccn[:,:,i], cmap=plt.cm.gray)
    
    # Save mean
    plt.imsave('analysis/occ_mean.jpg', occ.mean(2), cmap=plt.cm.gray)
    plt.imsave('analysis/noocc_mean.jpg', noocc.mean(2), cmap=plt.cm.gray)
    
    # Create nii data
    occimgs = glob.glob('imgs/*_occ.jpg')
    nooccimgs = glob.glob('imgs/*_noocc.jpg')
    
    # occ
    occnii, occfiles, prng = transform.img2nii(
            occimgs, jit=(8,18), clean=True, null=False, prng=prng
            )
    nb.save(occnii, "nii/occ.nii")
    np.savetxt("nii/occ.txt", 
            np.asarray(occfiles).transpose(), delimiter=",", fmt="%s"
            )
    
    # noocc
    nooccnii, nooccfiles, prng = transform.img2nii(
            nooccimgs, jit=(8,18), clean=True, null=False, prng=prng
            )
            
    nb.save(nooccnii, "nii/noocc.nii")
    np.savetxt("nii/noocc.txt", 
            np.asarray(nooccfiles).transpose(), delimiter=",", fmt="%s"
            )

    
def test_predict():
    
    # Assumes test_data() has run...
    proc = subprocess.Popen('python ../bin/predict.py nii/noocc.nii nii/noocc.txt imgs/*_occ.jpg results/noocc_pred_occ_betas.jpg results/occ_pred_nocc_preds.jpg', shell=True)
    out, err = proc.communicate()
    print(out)
    print(err)

    