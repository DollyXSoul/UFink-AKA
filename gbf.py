import hashlib
import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GBF_FILE = os.path.join(BASE_DIR, "gbf_storage.json")
CGBF_FILE = os.path.join(BASE_DIR, "cgbf_storage.json")


class GarbledBloomFilter:

    def __init__(self, size=256, k=3):
        self.size = size
        self.k = k

        if os.path.exists(GBF_FILE):
            with open(GBF_FILE, "r") as f:
                data = json.load(f)
            self.table = [int(x) if x is not None else None for x in data]
        else:
            self.table = [None] * size

    def _hashes(self, key):

        indices = []

        for i in range(self.k):
            h = hashlib.sha256((key + str(i)).encode()).hexdigest()
            indices.append(int(h, 16) % self.size)

        return indices

    def insert(self, key, value):

        indices = self._hashes(key)

        for idx in indices:
            self.table[idx] = value

        self.save()

    def retrieve(self, key):

        indices = self._hashes(key)

        values = []

        for idx in indices:
            v = self.table[idx]
            if v is None:
                return None
            values.append(v)

        # ensure consistency
        if all(v == values[0] for v in values):
            return values[0]

        return None

    def save(self):

        with open(GBF_FILE, "w") as f:
            json.dump(self.table, f)


class CountingGarbledBloomFilter:

    def __init__(self, size=1024, k=3):
        self.size = size
        self.k = k

        if os.path.exists(CGBF_FILE):
            with open(CGBF_FILE, "r") as f:
                data = json.load(f)

            if isinstance(data, list):
                self.table = data
            else:
                print("[WARNING] Invalid GBF format, reinitializing")
                self.table = [{} for _ in range(size)]
        else:
            self.table = [{} for _ in range(size)]

    # -----------------------------
    # Hash Functions
    # -----------------------------
    def _hashes(self, key):
        hashes = []
        for i in range(self.k):
            h = hashlib.sha256((key + str(i)).encode()).hexdigest()
            idx = int(h, 16) % self.size
            hashes.append(idx)
        return hashes

    # -----------------------------
    # Insert
    # -----------------------------
    def insert(self, key, value):
        indices = self._hashes(key)

        for idx in indices:
            slot = self.table[idx]
            slot[value] = slot.get(value, 0) + 1

    # -----------------------------
    # Retrieve
    # -----------------------------
    def retrieve(self, key):
        indices = self._hashes(key)

        sets = []

        for idx in indices:
            slot = self.table[idx]
            if not slot:
                # return any value (same across hashes ideally)
                return None
            sets.append(set(slot.keys()))

        common = set.intersection(*sets)

        if common:
            return next(iter(common))

        return None

    # -----------------------------
    # Optimized Update (SINGLE PASS)
    # -----------------------------
    def update(self, key, old_value, new_value):
        indices = self._hashes(key)

        for idx in indices:
            slot = self.table[idx]

            # remove old value
            if old_value in slot:
                slot[old_value] -= 1
                if slot[old_value] == 0:
                    del slot[old_value]

            # insert new value
            slot[new_value] = slot.get(new_value, 0) + 1

    # -----------------------------
    # Save to file (CALL ONCE)
    # -----------------------------
    def save(self):
        with open(CGBF_FILE, "w") as f:
            json.dump(self.table, f)
