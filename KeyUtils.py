# KeyUtils.py
# --------------------------------------------------------
# This file handles key generation, saving, loading, and
# updating. Keys are 128-bit binary strings.

import random

def generate_key(bits=128):
    """Generate a random binary string of given length."""
    return ''.join(random.choice('01') for _ in range(bits))

def write_keys(filename, K1, K2, rounds):
    """Save keys and rounds to a text file."""
    with open(filename, "w") as f:
        f.write(K1 + "\n")
        f.write(K2 + "\n")
        f.write(str(rounds) + "\n")

def read_keys(filename):
    """Read keys and rounds from a text file."""
    with open(filename, "r") as f:
        lines = f.readlines()
    return lines[0].strip(), lines[1].strip(), int(lines[2].strip())

def reduce_key(key, drop_every=4):
    """Reduce 128-bit key → 96-bit key by dropping every 4th bit."""
    return ''.join([bit for i, bit in enumerate(key) if (i+1) % drop_every != 0])

def update_key(K1, K2):
    """Update keys using simple shift + XOR + bit flip (paper logic)."""
    # Left circular shift by 1
    K1 = K1[1:] + K1[0]
    K2 = K2[1:] + K2[0]

    # XOR first half with second half
    half = len(K1)//2
    K1 = ''.join(['0' if K1[i]==K1[i+half] else '1' for i in range(half)]) + K1[half:]
    half = len(K2)//2
    K2 = ''.join(['0' if K2[i]==K2[i+half] else '1' for i in range(half)]) + K2[half:]

    # Flip last bit
    K1 = K1[:-1] + ('0' if K1[-1]=='1' else '1')
    K2 = K2[:-1] + ('0' if K2[-1]=='1' else '1')

    return K1, K2
