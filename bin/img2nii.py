import argparse
import numpy as np
import nibabel as nb

from sklearn import linear_model, svm, tree

from objectify.transform import img2nii

parser = argparse.ArgumentParser(
        description=("Transform images into a set of simuluated BOLD"
        " timecourses, one timecourse per pixel"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
parser.add_argument(
        "images",
        nargs='+',
        help="Image files to be transformed into mock BOLD data"
        )
parser.add_argument(
        "niiname", type=str,
        help="Name of the nifti data file to save"
        )
parser.add_argument(
        "txtname", type=str,
        help="Name of the csv that will index images onsets in the nifti data"
        )
parser.add_argument(
        "--no_clean",
        action="store_false",
        dest="clean",
        help="Zero out pixels with (nearly) no variance."
        )
parser.add_argument(
        "--null",
        action="store_true",
        dest="null",
        help="Pixels in each image are shuffled, creating 'null' images"
        )
parser.add_argument(
        "--seed",
        default=42, type=int,
        help="RandomState seed"
        )
parser.set_defaults(clean=True)
parser.set_defaults(null=False)
args = parser.parse_args()

prng = np.random.RandomState(args.seed)

# Get images and conver them
nii, files, prng = img2nii(args.images, 
        jit=(8,18), clean=args.clean, null=args.null, prng=prng
        )
nb.save(nii, args.niiname)

# Save csv
np.savetxt(args.txtname, 
    np.asarray(files).transpose(), delimiter=",", fmt="%s"
    )
