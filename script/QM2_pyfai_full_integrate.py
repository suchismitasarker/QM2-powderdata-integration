# Test script for integrating Pilatus6M images at CHESS beamline ID4B
# Written by Nathan S Johnson 05/16/2023
# Written and Updated  by Suchismita Sarker 03/05/2026
# Enhanced version: plotting, logging, Q→2θ conversion, caking, mask support

import pyFAI
import numpy as np
import pandas as pd
import sys
import glob
import os
import fabio
import matplotlib.pyplot as plt


# -----------------------------
# LOAD MASK FILE
# -----------------------------
def load_mask(mask_path):
    if mask_path is None:
        return None

    print("RAW mask path:", repr(mask_path))

    # Remove whitespace and invisible characters
    mask_path = mask_path.strip()
    mask_path = mask_path.replace("\u00A0", "")  # non-breaking space
    mask_path = mask_path.replace("\t", "")      # tabs
    mask_path = mask_path.replace("\n", "")      # newlines
    mask_path = mask_path.replace("\r", "")      # carriage returns

    print("CLEANED mask path:", repr(mask_path))

    ext = os.path.splitext(mask_path)[1].lower()
    print("Detected extension:", repr(ext))

    if ext in [".tif", ".tiff", ".cbf", ".edf"]:
        mask = fabio.open(mask_path).data.astype(bool)
    elif ext == ".npy":
        mask = np.load(mask_path).astype(bool)
    else:
        raise ValueError(f"Unsupported mask format: {ext}")

    return mask


# -----------------------------
# 1D INTEGRATION
# -----------------------------
def data_reduction(imgPath, poniPath, exportBase, mask_array=None, thbin=10000):

    imArray = fabio.open(imgPath).data.astype('uint32')
    ai = pyFAI.load(poniPath)

    # detector saturation mask
    sat_mask = (imArray > 65530) | (imArray <= 0)

    # merge with user mask
    if mask_array is not None:
        if mask_array.shape != imArray.shape:
            raise ValueError("Mask shape does not match detector image shape.")
        full_mask = sat_mask | mask_array
    else:
        full_mask = sat_mask

    x, I = ai.integrate1d(imArray, thbin, mask=full_mask, unit="q_A^-1")

    df = pd.DataFrame({'x': x, 'I': I})
    df.to_csv(exportBase + "_Q.csv", index=False)

    plt.figure(figsize=(6,4))
    plt.plot(x, I, lw=1)
    plt.xlabel("Q (Å⁻¹)")
    plt.ylabel("Intensity")
    plt.title(os.path.basename(imgPath))
    plt.xlim(2, 10)
    plt.tight_layout()
    plt.savefig(exportBase + "_plot.png", dpi=150)
    plt.close()

    return x, I


# -----------------------------
# Q → 2θ CONVERSION + PLOT
# -----------------------------
def convert_q_to_tth(q, I, poniPath, exportBase):
    ai = pyFAI.load(poniPath)
    wavelength = ai.wavelength  # meters

    tth_rad = 2 * np.arcsin(q * wavelength / (4 * np.pi))
    tth_deg = np.degrees(tth_rad)

    df = pd.DataFrame({'2theta_deg': tth_deg, 'I': I})
    df.to_csv(exportBase + "_2theta.csv", index=False)

    plt.figure(figsize=(6,4))
    plt.plot(tth_deg, I, lw=1)
    plt.xlabel("2θ (deg)")
    plt.ylabel("Intensity")
    plt.title(os.path.basename(exportBase) + " (2θ)")
    plt.xlim(tth_deg.min(), tth_deg.max())
    plt.tight_layout()
    plt.savefig(exportBase + "_2theta_plot.png", dpi=150)
    plt.close()

    return tth_deg


# -----------------------------
# CAKING (2D INTEGRATION)
# -----------------------------
def perform_caking(imgPath, poniPath, exportBase, mask_array=None, nrad=2000, nazim=360):

    imArray = fabio.open(imgPath).data.astype('uint32')
    ai = pyFAI.load(poniPath)

    sat_mask = (imArray > 65530) | (imArray <= 0)

    if mask_array is not None:
        full_mask = sat_mask | mask_array
    else:
        full_mask = sat_mask

    cake, tth, chi = ai.integrate2d(
        imArray,
        npt_rad=nrad,
        npt_azim=nazim,
        unit="2th_deg",
        mask=full_mask
    )

    np.save(exportBase + "_cake.npy", cake)

    plt.figure(figsize=(6,5))
    plt.imshow(
        cake,
        extent=[chi.min(), chi.max(), tth.max(), tth.min()],
        aspect='auto',
        cmap='viridis',
        vmin=0,
        vmax=np.percentile(cake, 99)
    )
    plt.xlabel("Chi (deg)")
    plt.ylabel("2θ (deg)")
    plt.title("Caked: " + os.path.basename(imgPath))
    plt.xlim(-180, 180)
    plt.ylim(0, 20)
    plt.colorbar(label="Intensity")
    plt.tight_layout()
    plt.savefig(exportBase + "_cake.png", dpi=150)
    plt.close()

    return cake


# -----------------------------
# BATCH PROCESSING
# -----------------------------
def integrate_images(folderPath, poniPath, exportPath, maskPath=None):

    mask_array = load_mask(maskPath)

    imgPaths = sorted(glob.glob(os.path.join(folderPath, '*.cbf')))
    print("Found images:", imgPaths)

    log_entries = []

    for imgPath in imgPaths:

        base = os.path.basename(imgPath)
        label = os.path.splitext(base)[0]
        exportBase = os.path.join(exportPath, label)

        print("Processing:", imgPath)

        q, I = data_reduction(imgPath, poniPath, exportBase, mask_array)

        tth = convert_q_to_tth(q, I, poniPath, exportBase)

        cake = perform_caking(imgPath, poniPath, exportBase, mask_array)

        log_entries.append({
            "filename": base,
            "q_points": len(q),
            "cake_shape": cake.shape
        })

    log_df = pd.DataFrame(log_entries)
    log_df.to_csv(os.path.join(exportPath, "batch_log.csv"), index=False)

    print("Batch processing complete.")


# -----------------------------
# MAIN
# -----------------------------
# -----------------------------
# MAIN
# -----------------------------
# -----------------------------
# MAIN (interactive input)
# -----------------------------
if __name__ == "__main__":

    print("\n=== PyFAI Integration Script ===")
    print("Please enter the required paths.\n")

    folder = input("Image folder path: ").strip()
    poni   = input("PONI file path: ").strip()
    mask   = input("Mask file path (or leave blank for none): ").strip()
    out    = input("Output folder path: ").strip()

    if mask == "":
        mask = None

    print("\n--- Confirming paths ---")
    print("Image folder :", folder)
    print("PONI file    :", poni)
    print("Mask file    :", mask)
    print("Output folder:", out)
    print("-------------------------\n")

    integrate_images(folder, poni, out, mask)


