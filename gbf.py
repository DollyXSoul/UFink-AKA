import hashlib
import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GBF_FILE = os.path.join(BASE_DIR, "gbf_storage.json")


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
