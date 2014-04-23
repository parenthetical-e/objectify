import argparse
import numpy as np
import nibabel as nb

from skimage import io
from skimage import filter as filt
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
        description=("Average images"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
parser.add_argument(
        "nii",
        help="A Nifti1 data file"
        )
parser.add_argument(
        "name",
        help="Save mean as (extension defines image type)"
        )
parser.add_argument(
        "--no_smooth",
        action="store_false",
        dest='smooth',
        help="Don't apply a Gaussian smooth after averaging?"
        )
parser.add_argument(
        "--sigma", 
        default=12, type=int,
        help="Width of gaussian smooth"
        )
parser.set_defaults(smooth=True)        

args = parser.parse_args()

nii = nb.load(args.nii).get_data()
meanimg = nii.mean(axis=nii.ndim - 1)  
    ## Time/TR/vol is the last axis...

if args.smooth:
    meanimg = filt.gaussian_filter(meanimg, args.sigma)

plt.imsave(args.name, meanimg, cmap=plt.cm.gray)

