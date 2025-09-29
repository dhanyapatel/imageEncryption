# en_rbf.py
# --------------------------------------------------------
# Implements full encryption:
# 1. Rubik's cube scrambling
# 2. Bitplane decomposition
# 3. Frame rotation + shuffling
# 4. Reconstruction

from PIL import Image
import numpy as np
import KeyUtils

# ---------- Helper Functions ----------
def decompose_bitplanes(img):
    """Split RGB image into 24 bitplanes (8 per channel)."""
    arr = np.array(img)
    planes = []
    for c in range(3):  # R, G, B
        channel = arr[:, :, c]
        for bit in range(8):
            plane = ((channel >> bit) & 1).astype(np.uint8)
            planes.append(plane)
    return planes

def recompose_bitplanes(planes):
    """Rebuild RGB image from 24 bitplanes."""
    h, w = planes[0].shape
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for c in range(3):
        channel = np.zeros((h, w), dtype=np.uint8)
        for bit in range(8):
            channel |= (planes[c*8 + bit] << bit)
        arr[:, :, c] = channel
    return Image.fromarray(arr)

def rotate_frame(plane, steps):
    """Rotate outer frame clockwise by given steps."""
    mat = plane.copy()
    h, w = mat.shape
    for _ in range(steps):
        # Take border pixels
        top = mat[0, :].copy()
        right = mat[:, -1].copy()
        bottom = mat[-1, :].copy()
        left = mat[:, 0].copy()
        # Rotate clockwise
        mat[0, 1:] = top[:-1]
        mat[1:, -1] = right[:-1]
        mat[-1, :-1] = bottom[1:]
        mat[:-1, 0] = left[1:]
    return mat

# ---------- Main Encryption ----------
def encrypt_image_rbf(input_path, output_path, keyfile="keys_rbf.txt"):
    # Load input image
    img = Image.open(input_path).convert("RGB")

    # Generate and save keys
    K1 = KeyUtils.generate_key()
    K2 = KeyUtils.generate_key()
    rounds = 3  # 3 rounds of scrambling (block sizes 16, 32, 64)
    KeyUtils.write_keys(keyfile, K1, K2, rounds)
    print("✅ Keys saved to", keyfile)

    # Phase 1: (Simplified) Rubik-like scrambling (row/col rotations)
    arr = np.array(img)
    h, w, _ = arr.shape
    for _ in range(rounds):
        for i in range(h):
            shift = int(K1[i % len(K1)], 2) % w
            arr[i] = np.roll(arr[i], shift, axis=0)
        for j in range(w):
            shift = int(K2[j % len(K2)], 2) % h
            arr[:, j] = np.roll(arr[:, j], shift, axis=0)

    # Phase 2: Bitplane decomposition
    planes = decompose_bitplanes(Image.fromarray(arr))

    # Phase 3: Frame rotation + shuffling
    K1_red = KeyUtils.reduce_key(K1)
    K2_red = KeyUtils.reduce_key(K2)
    for idx, plane in enumerate(planes):
        steps = (int(K1_red[idx % len(K1_red)]) + int(K2_red[idx % len(K2_red)])) % 5
        planes[idx] = rotate_frame(plane, steps)

    # Shuffle planes: reverse order per channel
    planes[0:8] = planes[0:8][::-1]   # Blue
    planes[8:16] = planes[8:16][::-1] # Green
    planes[16:24] = planes[16:24][::-1] # Red

    # Phase 4: Reconstruction
    encrypted = recompose_bitplanes(planes)
    encrypted.save(output_path)
    encrypted.show()
    print("✅ Encrypted image saved as", output_path)

# ---------- Run directly ----------
if __name__ == "__main__":
    path = input("Enter image path: ").strip()
    encrypt_image_rbf(path, "encrypted.png")

