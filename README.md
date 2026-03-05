# QM2 Beamline - PyFAI-Based X‑ray Diffraction Integration Pipeline 

A complete workflow for CHESS ID4B Pilatus6M data: calibration, masking, 1D integration, 2D caking, and Q→2θ conversion.

# Overview 
This repository contains a Python workflow for processing Pilatus6M diffraction images collected at the CHESS ID4B beamline. It supports:

* Detector calibration using .poni files
* Batch processing of raw diffraction images
1D azimuthal integration (I vs Q)
Q → 2θ conversion (I vs 2θ)
2D caking (intensity vs χ and 2θ)
Mask file support (.edf, .tif, .cbf, .npy)
Automatic logging of processed files
Organized output folder structure
The workflow is built on pyFAI, fabio, NumPy, Pandas, and Matplotlib.
