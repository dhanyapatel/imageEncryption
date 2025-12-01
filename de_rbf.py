# de_rbf.py
from PIL import Image
import numpy as np
import KeyUtils
from en_rbf import decompose_bitplanes, recompose_bitplanes, rotate_frame

def decrypt_image_rbf(input_path, output_path, keyfile="keys_rbf.json"):
    # Load encrypted image
    img = Image.open(input_path).convert("RGB")

    # Read keys that were saved by encryption
    rounds, round_keys, final_keys = KeyUtils.read_keys(keyfile)
    print(f"🔑 Loaded {rounds} round-keys from {keyfile}")

    # Phase 1: bitplane decomposition
    planes = decompose_bitplanes(img)

    # Step: undo plane shuffling (same operation as encryption — reversing twice cancels)
    planes[0:8] = planes[0:8][::-1]      # R
    planes[8:16] = planes[8:16][::-1]    # G
    planes[16:24] = planes[16:24][::-1]  # B

    # Step: undo frame rotations using final_keys (reverse direction)
    K1_red = KeyUtils.reduce_key(final_keys[0])
    K2_red = KeyUtils.reduce_key(final_keys[1])
    for idx, plane in enumerate(planes):
        steps = (int(K1_red[idx % len(K1_red)]) + int(K2_red[idx % len(K2_red)])) % 5
        planes[idx] = rotate_frame(plane, -steps)

    # Recompose to RGB array
    recomposed = recompose_bitplanes(planes)
    arr = np.array(recomposed)
    h, w, _ = arr.shape

    # Step: undo Rubik-like scrambling in reverse round order using saved round_keys
    for r in reversed(range(rounds)):
        K1_r, K2_r = round_keys[r]
        # undo column rotations (vertical) in reverse order
        for j in reversed(range(w)):
            idx = (j * 4) % len(K2_r)
            bits = KeyUtils.get_bits(K2_r, idx, 4)
            shift = int(bits, 2) % h
            arr[:, j] = np.roll(arr[:, j], -shift, axis=0)

        # undo row rotations (horizontal) in reverse order
        for i in reversed(range(h)):
            idx = (i * 4) % len(K1_r)
            bits = KeyUtils.get_bits(K1_r, idx, 4)
            shift = int(bits, 2) % w
            arr[i] = np.roll(arr[i], -shift, axis=1)

    decrypted = Image.fromarray(arr)
    decrypted.save(output_path)
    print("✅ Decrypted saved as:", output_path)
    return output_path

if __name__ == "__main__":
    enc_path = input("Enter encrypted image path: ").strip()
    decrypt_image_rbf(enc_path, "decrypted.png")
