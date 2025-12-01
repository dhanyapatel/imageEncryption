# en_rbf.py
from PIL import Image
import numpy as np
import KeyUtils

# ---------- Helpers ----------
def decompose_bitplanes(img):
    """Split RGB image into 24 bitplanes (8 per channel). Order: R(0..7), G(0..7), B(0..7)."""
    arr = np.array(img)
    planes = []
    for c in range(3):  # 0=R,1=G,2=B
        channel = arr[:, :, c]
        for bit in range(8):
            plane = ((channel >> bit) & 1).astype(np.uint8)
            planes.append(plane)
    return planes

def recompose_bitplanes(planes):
    """Rebuild RGB image from 24 bitplanes (same order as decompose)."""
    h, w = planes[0].shape
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for c in range(3):
        channel = np.zeros((h, w), dtype=np.uint8)
        for bit in range(8):
            channel |= (planes[c*8 + bit] << bit)
        arr[:, :, c] = channel
    return Image.fromarray(arr)

def rotate_frame(plane, steps):
    """Rotate outer 1-pixel border by steps (positive = clockwise)."""
    mat = plane.copy()
    h, w = mat.shape
    if h < 2 or w < 2:
        return mat
    total = 2 * (h + w) - 4
    steps = int(steps) % total

    # Extract border in order: top (left→right), right (top+1→bottom-1), bottom (right→left), left (bottom-1→top+1)
    top = mat[0, :].astype(np.uint8)
    right = mat[1:h-1, -1].astype(np.uint8) if h > 2 else np.array([], dtype=np.uint8)
    bottom = mat[-1, ::-1].astype(np.uint8)
    left = mat[h-2:0:-1, 0].astype(np.uint8) if h > 2 else np.array([], dtype=np.uint8)

    border = np.concatenate([top, right, bottom, left])
    border = np.roll(border, steps)

    idx = 0
    mat[0, :] = border[idx: idx + w]; idx += w
    if h > 2:
        mat[1:h-1, -1] = border[idx: idx + (h - 2)]; idx += (h - 2)
    mat[-1, :] = border[idx: idx + w][::-1]; idx += w
    if h > 2:
        mat[h-2:0:-1, 0] = border[idx: idx + (h - 2)]
    return mat

# ---------- Main Encryption ----------
def encrypt_image_rbf(input_path, output_path, keyfile="keys_rbf.json", rounds=3):
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape

    # Generate initial keys
    K1 = KeyUtils.generate_key()
    K2 = KeyUtils.generate_key()

    # Apply rounds; store the keys used in each round (before update)
    round_keys = []
    K1_cur, K2_cur = K1, K2
    for r in range(rounds):
        # Row rotations (horizontal)
        for i in range(h):
            idx = (i * 4) % len(K1_cur)
            bits = KeyUtils.get_bits(K1_cur, idx, 4)
            shift = int(bits, 2) % w
            arr[i] = np.roll(arr[i], shift, axis=1)

        # Column rotations (vertical)
        for j in range(w):
            idx = (j * 4) % len(K2_cur)
            bits = KeyUtils.get_bits(K2_cur, idx, 4)
            shift = int(bits, 2) % h
            arr[:, j] = np.roll(arr[:, j], shift, axis=0)

        round_keys.append((K1_cur, K2_cur))
        # update keys for next round
        K1_cur, K2_cur = KeyUtils.update_key(K1_cur, K2_cur)

    # final keys (after rounds) used for bitplane/frame ops
    final_keys = (K1_cur, K2_cur)

    # Phase: bitplane decomposition
    planes = decompose_bitplanes(Image.fromarray(arr))

    # Frame rotation per plane (use final_keys reduced)
    K1_red = KeyUtils.reduce_key(final_keys[0])
    K2_red = KeyUtils.reduce_key(final_keys[1])
    for idx, plane in enumerate(planes):
        # using single-bit sum modulo 5 (keeps same behaviour but deterministic)
        steps = (int(K1_red[idx % len(K1_red)]) + int(K2_red[idx % len(K2_red)])) % 5
        planes[idx] = rotate_frame(plane, steps)

    # Shuffle planes: reverse order per channel (R, G, B groups)
    planes[0:8] = planes[0:8][::-1]      # R
    planes[8:16] = planes[8:16][::-1]    # G
    planes[16:24] = planes[16:24][::-1]  # B

    # Reconstruct and save
    encrypted = recompose_bitplanes(planes)
    encrypted.save(output_path)
    print(" Encrypted saved as:", output_path)

    # Save keys (all round keys + final keys) so decryption is exact
    KeyUtils.write_keys(keyfile, round_keys, final_keys)
    print(" Keys saved to:", keyfile)

if __name__ == "__main__":
    img_path = input("Enter image path to encrypt: ").strip()
    encrypt_image_rbf(img_path, "encrypted.png")
