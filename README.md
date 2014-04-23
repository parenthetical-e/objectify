# Install

Put in in a dir on your [$PYTHONPATH](https://docs.python.org/2/using/cmdline.html)

# Depends

* numpy
* pandas
* sklearn
* skimage

Which can be had by installing [anaconda](https://store.continuum.io/cshop/anaconda/)

also install

* nibabel - `pip install nibabel`

It also depends in a bunch of EJP's code, which can be found on github

* modelmodel - https://github.com/andsoandso/modelmodel.git
* fmrilearn - https://github.com/andsoandso/fmrilearn.git

`git clone` these into suitable dirs on the $PYTHONPATH


# API

See code.

# Programs

In `objectify/bin/..` are several program that will let you run (useful combinations) API functions from the commandline, i.e bash.  I outline there usage below.

## img2nii

Converts a list or glob of images (in order) to a mock BOLD timecourse, saved as Nifit1. 

	usage: img2nii.py [-h] [--no_clean] [--null] [--seed SEED]
	                  images [images ...] niiname txtname

	Transform images into a set of simuluated BOLD timecourses, one timecourse per
	pixel

	positional arguments:
	  images       Image files to be transformed into mock BOLD data
	  niiname      Name of the nifti data file to save
	  txtname      Name of the csv that will index images onsets in the nifti data

	optional arguments:
	  -h, --help   show this help message and exit
	  --no_clean   Zero out pixels with (nearly) no variance. (default: True)
	  --null       Pixels in each image are shuffled, creating 'null' images
	               (default: False)
	  --seed SEED  RandomState seed (default: 42)

	
By example:
		
		python objectify/bin/img2nii.py \
			stim/Occ_noise_gray1_V_*.gif \
			data/imgs.nii \
			data/imgs.txt


## predict

	usage: predict.py [-h] [--window WINDOW] [--model MODEL] [--no_clean]
	                  [--seed SEED]
	                  nii onset images [images ...] betaname predname

	Predict an image stack with fMRI data

	positional arguments:
	  nii              Nifti file name
	  onset            Text file denoteing img onset, by name.
	  images           A list of images to predict
	  betaname         Save Beta values as (extension defines image type)
	  predname         Save predicted images as (extension defines image type).

	optional arguments:
	  -h, --help       show this help message and exit
	  --window WINDOW  Trial window size (in TRs) (default: 8)
	  --model MODEL    A regression (sklearn) regression object name that
	                   implments .fit() and .predict() (default: LinearRegression)
	  --no_clean       Zero out pixels with (nearly) no variance. (default: True)
	  --seed SEED      RandomState seed (default: 42)

By example

Occ as bold and image
	
	python objectify/bin/predict.py \
		data/Occ_noise_gray1_H.nii \
		data/Occ_noise_gray1_H.txt \
		stim/Occ_noise_gray1_H*.gif \
		results/b_Occ_noise_gray1_H_i_Occ_noise_gray1_H_betas.gif \
		results/b_Occ_noise_gray1_H_i_Occ_noise_gray1_H_betas_preds.gif

Occ BOLD. NoOcc as image.

	python objectify/bin/predict.py \
		data/Occ_noise_gray1_H.nii \
		data/Occ_noise_gray1_H.txt \
		stim/NoOcc_noise_gray1_H*.gif \
		results/b_Occ_noise_gray1_H_i_NoOcc_noise_gray1_H_betas.gif \
		results/b_Occ_noise_gray1_H_i_NoOcc_noise_gray1_H_betas_preds.gif

		
## img2mean

	Average images

	positional arguments:
	  images         Image files
	  name           Save mean as (extension defines image type)

	optional arguments:
	  -h, --help     show this help message and exit
	  --no_smooth    Don't apply a Gaussian smooth after averaging? (default:
	                 True)
	  --sigma SIGMA  Width of gaussian smooth (default: 12)

By example

Average

	python objectify/bin/img2mean.py \
		stim/Occ_noise_gray1_H*.gif \
		analysis/Occ_test.gif

Average without Gaussian smooth

	python objectify/bin/img2mean.py \
		stim/Occ_noise_gray1_H*.gif \
		analysis/Occ_test.gif \
		--no_smooth

Average but change degreee of smooth

Very little

	python objectify/bin/img2mean.py \
		stim/Occ_noise_gray1_H*.gif \
		analysis/Occ_test.gif \
		--sigma 2
		
A lot

	python objectify/bin/img2mean.py \
		stim/Occ_noise_gray1_H*.gif \
		analysis/Occ_test.gif \
		--sigma 20
		

## nii2mean

	usage: nii2mean.py [-h] [--no_smooth] [--sigma SIGMA] nii name

	Average images

	positional arguments:
	  nii            A Nifti1 data file
	  name           Save mean as (extension defines image type)

	optional arguments:
	  -h, --help     show this help message and exit
	  --no_smooth    Don't apply a Gaussian smooth after averaging? (default:
	                 True)
	  --sigma SIGMA  Width of gaussian smooth (default: 12)
