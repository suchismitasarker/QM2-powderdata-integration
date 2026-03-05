## Accessing the Environment

You can run the integration either from a terminal on lnx201 or from JupyterHub different node.
Activate the base Conda installation:

```
source /nfs/chess/sw/anaconda3_nsj/miniconda/bin/activate

```
## Check available environments:

```
conda env list
```

## Expected output:
```
# conda environments:
#
base                  *  /nfs/chess/sw/anaconda3_nsj/miniconda
HiTp                     /nfs/chess/sw/anaconda3_nsj/miniconda/envs/HiTp
```
## Activate the HiTp environment:

```
conda activate HiTp
```
## Navigate to the Code Location
```
cd /nfs/chess/id4baux/suchi
```

## Full Integration With Mask File

```
QM2_pyfai_full_integrate.py

```
## Running the code from the terminal
```
python QM2_pyfai_full_integrate.py

It will ask for 
Image folder path:  
PONI file path:  
Mask file path (optional, if yes, provide the filename):
Output folder path:  


```

Output folder path:  

