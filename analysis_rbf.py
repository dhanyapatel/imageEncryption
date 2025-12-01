# analysis_rbf.py
# --------------------------------------------------------
# Performs:
# 1. Histogram analysis for original, encrypted, decrypted
# 2. PSNR between original ↔ encrypted, original ↔ decrypted

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# ---------- Helper: load as grayscale ----------
def load_grayscale(path):
    img = Image.open(path).convert("L")  # convert to grayscale
    return np.array(img)

# ---------- PSNR ----------
def compute_psnr(img1, img2):
    """Compute PSNR between two images (numpy arrays, uint8)."""
    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)

    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return float("inf")
    PIXEL_MAX = 255.0
    psnr = 20 * np.log10(PIXEL_MAX / np.sqrt(mse))
    return psnr

# ---------- Histogram plotting ----------
def plot_histogram(img, title):
    """Plot histogram of a grayscale image."""
    flat = img.flatten()
    plt.hist(flat, bins=256, range=(0, 255))
    plt.title(title)
    plt.xlabel("Pixel Intensity (0–255)")
    plt.ylabel("Frequency")

# ---------- Full analysis ----------
def run_full_analysis(original_path, encrypted_path, decrypted_path):
    # Load images
    orig = load_grayscale(original_path)
    enc = load_grayscale(encrypted_path)
    dec = load_grayscale(decrypted_path)

    # ---- PSNR ----
    psnr_orig_enc = compute_psnr(orig, enc)
    psnr_orig_dec = compute_psnr(orig, dec)

    print("📊 PSNR Results")
    print(f"  PSNR (Original vs Encrypted): {psnr_orig_enc:.4f} dB")
    print(f"  PSNR (Original vs Decrypted): {psnr_orig_dec:.4f} dB")

    # ---- Histograms ----
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plot_histogram(orig, "Original Image Histogram")

    plt.subplot(1, 3, 2)
    plot_histogram(enc, "Encrypted Image Histogram")

    plt.subplot(1, 3, 3)
    plot_histogram(dec, "Decrypted Image Histogram")

    plt.tight_layout()
    plt.show()

# ---------- Run directly ----------
# ---------- Run directly ----------
if __name__ == "__main__":
    # Ask only for ORIGINAL image path
    original_path = input("Enter path of ORIGINAL image: ").strip()

    # Keep these fixed (or change manually)
    encrypted_path = "encrypted.png"
    decrypted_path = "decrypted.png"

    run_full_analysis(original_path, encrypted_path, decrypted_path)

