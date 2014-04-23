import argparse
import numpy as np
import nibabel as nb

import matplotlib.pyplot as plt
from skimage import io
from skimage import filter as filt

parser = argparse.ArgumentParser(
        description=("Average images"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
parser.add_argument(
        "images",
        nargs='+',
        help="Image files"
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


images = io.ImageCollection(args.images)
files = images.files
images = images.concatenate().astype(np.float)

if images.ndim == 4:
    images = images[:,:,:,0]  ## If RGB
elif (images.ndim < 2) or (images.ndim > 4):
    raise ValueError("To few images.")

t_img, x_img, y_img = images.shape

meanimg = images.mean(0)

if args.smooth:
    meanimg = filt.gaussian_filter(meanimg, args.sigma)

plt.imsave(args.name, meanimg, cmap=plt.cm.gray)

