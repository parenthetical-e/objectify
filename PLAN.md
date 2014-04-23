# Simulation

How much noise is needed in a 'gap' to call it a continuous object? Let's take a few theoretical views.

## Exogenous

### Percolation

Assume the brain attempts to group separate objects (defined later) using the any minimal complete path between them. If the complete path exists, do objectification.

* Contrast based segmentation to get pre-objects,
* Or simpler contrast segmentation to get sets of lines.
* Look for paths between any (parallel?) lines
* Use percolation theory to look for paths.  
* Percolation requires binary data. 
 - Need to map grey scale to (0,1)
 - Can this task be redone using only (0,1)?

* Percolation provides a theoretical limit on objectification (42.5?).

 The theoretical (bottom up, no expectation) minimum is the percolation number?  The human amount is?

How to implement a simple model with prior expectations? SDT?

### Diffusion

I'd like to give this a go, but not sure how to do setup the decision space in a pure exogenous take.

## Endogenous

### SDT

Assume the brain has some templates for the possible objectifications.  Take everything inside and call it a distribution.  Do any of objectification distribution differ from the null?

* Draw boxes for differ objectifications, create dists
* Do null SDT
* Or do paired-wise SDT, following up significance with a selection (mean based?)

# Regression

The trial-level BOLD data to predict the trial-level pixels, by regression.

## No retinotopy
### Blind, with a clock

Try all pixel-bold combinations. Rank to find best mapping. Trial TRs each get their own model (hence the t hung off `x_bold_t`).

		x_pixel = B * x_bold_t

### Blind, with a scale

Try all pixel-bold combinations. Rank to find best mapping. This time we take a measure over each trial's bold response, and do the regression with that.


## Retinotopy
### 1:1 by affine

Solve alignment between image and bold, borrowing methods from fMRI (e.g. Mitchell or Haxby's attempts at inter subject alignment).  The do simple linear regression. Mapping is 1:1.

###  N:1 by affine

Try and olve alignment between image and bold, but realize it will be imperfect. To try and compensate we use a N voxel spotlight to regress onto the `x_pixel`. 