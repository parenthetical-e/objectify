import os
import shutil
import argparse
import numpy as np
import nibabel as nb

import matplotlib.pyplot as plt

from skimage import io
from sklearn import linear_model, svm, tree

from modelmodel.behave import trials
from modelmodel.noise import white
from modelmodel.hrf import double_gamma as dg
from modelmodel.bold import create_bold
from fmrilearn.preprocess.data import find_good_features
from fmrilearn.preprocess.reshape import by_trial 

from objectify.transform import reshape2d, undo2d, trial_space, norm
from objectify.io import load_y, files2onsets


parser = argparse.ArgumentParser(
        description="Predict an image stack with fMRI data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
parser.add_argument(
        "nii",
        help="Nifti file name"
        )
parser.add_argument(
        "onset",
        help="Text file denoteing img onset, by name."
        )
parser.add_argument(
        "images",
        nargs='+',
        help="A list of images to predict"
        )
parser.add_argument(
        "betaname", type=str,
        help="Save Beta values as (extension defines image type)"
        )
parser.add_argument(
        "predname", type=str,
        help="Save predicted images as (extension defines image type)."
        )
parser.add_argument(
        "--window",
        default=8,
        help="Trial window size (in TRs)"
        )
parser.add_argument(
        "--model",
        default='LinearRegression',
        help="A regression (sklearn) regression object name that implments .fit() and .predict()"
        )
# parser.add_argument(
#         "--args",
#         default=None,
#         help="Positional arguments for --model"
#         )
# parser.add_argument(
#         "--kwargs",
#         default=None,
#         help="Keyword arguments for --model"
#         )
parser.add_argument(
        "--no_clean",
        action="store_false",
        dest="clean",
        help="Zero out pixels with (nearly) no variance."
        )
parser.add_argument(
        "--seed",
        default=42, type=int,
        help="RandomState seed"
        )
parser.set_defaults(clean=True)
args = parser.parse_args()

prng = np.random.RandomState(args.seed)

# Try HARD to load a sklearn regression object
try:
    Clf = getattr(linear_model, args.model)
except AttributeError:
    try:
        Clf = getattr(svm, args.model)
    except AttributeError:
        try:
            Clf = getattr(tree, args.model)
        except AttributeError:
            raise ValueError("--model not known")
clf = Clf()

# Get BOLD data and stim onsets
nii = nb.load(args.nii).get_data()
x_bold, y_bold, t_bold = nii.shape

files = load_y(args.onset)
onsets, trial_index = files2onsets(files)

# Get the images
images = io.ImageCollection(args.images)
files = images.files

# Convert to array
images = images.concatenate().astype(np.float)
if images.ndim == 4:
    images = images[:,:,:,0]
elif (images.ndim < 2) or (images.ndim > 4):
    raise ValueError("To few images.")

t_img, x_img, y_img = images.shape

# Sanity
if (x_bold, y_bold) != (x_img, y_img):
    raise ValueError("nii and images don't match in (x, y)")

# Convert both images and nii to X (n_sample, n_feature) format
## lets me use several (key) fmrilearn functions
Xnii = reshape2d(nii, axis=2)
Ximgs = reshape2d(images)
if Xnii.shape[1] != Ximgs.shape[1]:
    raise ValueError("Xs don't match")

# Fing non-zero variance features, i.e. good
if args.clean:
    good_nii = find_good_features(Xnii, sparse=False)
    good_y = find_good_features(Ximgs, sparse=False)
    good = list(set(good_nii).intersection(set(good_y)))
else:
    good = range(Xnii.shape[1])

Ximgs[:,good] = norm(Ximgs[:,good]) ## Norm for consistency with img2nii

# Predict!
Xbetas = np.zeros([args.window, Xnii.shape[1]])         ## Sparse?
Xpred = np.zeros([Ximgs.shape[0], Xnii.shape[1]])       ## Sparse?
for j in good:
    xtrial = trial_space(Xnii[:,j], onsets, args.window)
    clf.fit(xtrial, Ximgs[:,j])
    
    Xbetas[:,j] = clf.coef_
    Xpred[:,j] = clf.predict(xtrial)

# Back to 3d and save    
betas = undo2d(Xbetas, x_img, y_img)
preds = undo2d(Xpred, x_img, y_img)

for z in range(betas.shape[0]):
    head, tail = os.path.split(args.betaname)
    plt.imsave(
        os.path.join(head, str(z) + "_" + tail), betas[z,:,:], 
        cmap=plt.cm.gray
        )

for z in range(preds.shape[0]):
    head, tail = os.path.split(args.predname)
    plt.imsave(
        os.path.join(head, str(z) + "_" + tail), preds[z,:,:],
        cmap=plt.cm.gray
        )
    