# de_rbf.py
# --------------------------------------------------------
# Reverses encryption:
# 1. Reverse bitplane shuffling
# 2. Reverse frame rotations
# 3. Rebuild image
# 4. Reverse Rubik-like scrambling

from PIL import Image
import numpy as np
import os, glob
import KeyUtils
from en_rbf import decompose_bitplanes, recompose_bitplanes, rotate_frame

def decrypt_image_rbf(input_path, output_path, keyfile="keys_rbf.txt"):
    # Load encrypted image
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img)

    # Read keys
    K1, K2, rounds = KeyUtils.read_keys(keyfile)
    K1_red = KeyUtils.reduce_key(K1)
    K2_red = KeyUtils.reduce_key(K2)

    # Phase 1: Bitplane decomposition
    planes = decompose_bitplanes(img)

    # Reverse shuffle
    planes[0:8] = planes[0:8][::-1]   # Blue
    planes[8:16] = planes[8:16][::-1] # Green
    planes[16:24] = planes[16:24][::-1] # Red

    # Reverse frame rotation
    for idx, plane in enumerate(planes):
        steps = (int(K1_red[idx % len(K1_red)]) + int(K2_red[idx % len(K2_red)])) % 5
        planes[idx] = rotate_frame(plane, -steps)  # reverse

    # Reconstruct partially decrypted image
    arr = np.array(recompose_bitplanes(planes))

    # Reverse Rubik-like scrambling
    h, w, _ = arr.shape
    for _ in range(rounds):
        for j in range(w):
            shift = int(K2[j % len(K2)], 2) % h
            arr[:, j] = np.roll(arr[:, j], -shift, axis=0)
        for i in range(h):
            shift = int(K1[i % len(K1)], 2) % w
            arr[i] = np.roll(arr[i], -shift, axis=0)

    # Save final decrypted image
    decrypted = Image.fromarray(arr)
    decrypted.save(output_path)
    decrypted.show()
    print("✅ Decrypted image saved as", output_path)

# ---------- Run directly ----------
if __name__ == "__main__":
    encrypted_images = glob.glob("*.png")
    if not encrypted_images:
        print("❌ No encrypted image found!")
    else:
        latest = max(encrypted_images, key=os.path.getmtime)
        print("🖼 Using latest image:", latest)
        decrypt_image_rbf(latest, "decrypted.png")

