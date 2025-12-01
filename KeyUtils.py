# KeyUtils.py
import random
import json

def generate_key(bits=128):
    """Generate a random binary string of given length."""
    return ''.join(random.choice('01') for _ in range(bits))

def reduce_key(key, drop_every=4):
    """Reduce key by dropping every drop_every-th bit (deterministic)."""
    return ''.join([bit for i, bit in enumerate(key) if (i+1) % drop_every != 0])

def update_key(K1, K2):
    """Simple deterministic update (used in encryption rounds)."""
    # Left circular shift by 1
    K1 = K1[1:] + K1[0]
    K2 = K2[1:] + K2[0]

    # XOR first half with second half (produces new first half)
    half = len(K1) // 2
    K1 = ''.join(['0' if K1[i] == K1[i + half] else '1' for i in range(half)]) + K1[half:]
    half = len(K2) // 2
    K2 = ''.join(['0' if K2[i] == K2[i + half] else '1' for i in range(half)]) + K2[half:]

    # Flip last bit
    K1 = K1[:-1] + ('0' if K1[-1] == '1' else '1')
    K2 = K2[:-1] + ('0' if K2[-1] == '1' else '1')

    return K1, K2

def get_bits(key, start, n):
    """Return n bits from key starting at start (wrap-around)."""
    L = len(key)
    bits = [key[(start + i) % L] for i in range(n)]
    return ''.join(bits)

def write_keys(filename, round_keys, final_keys):
    """
    Save keys. Format (JSON):
    { "rounds": N,
      "round_keys": [{"K1": "...","K2":"..."}, ...],   # keys used in each round (before update)
      "final_keys": {"K1":"...","K2":"..."}            # keys used for bitplane/frame ops
    }
    """
    data = {
        "rounds": len(round_keys),
        "round_keys": [{"K1": r[0], "K2": r[1]} for r in round_keys],
        "final_keys": {"K1": final_keys[0], "K2": final_keys[1]}
    }
    with open(filename, "w") as f:
        json.dump(data, f)

def read_keys(filename):
    """Read the JSON keys file and return (rounds, round_keys_list, final_keys_tuple)."""
    with open(filename, "r") as f:
        data = json.load(f)
    rounds = data["rounds"]
    round_keys = [(r["K1"], r["K2"]) for r in data["round_keys"]]
    final = (data["final_keys"]["K1"], data["final_keys"]["K2"])
    return rounds, round_keys, final
