""" class added to encapsulate simhashing """

from hashlib import sha1


class SimHash:
    def __init__(self):
        self.fingerprints = []

    @staticmethod
    def create_fingerprint(page_content):
        num_bits = 160
        hex_scale = 16
        ini_hashes = []
        page_words = []
        vector_values = [0] * num_bits
        # hash all words
        for word in page_content:
            page_words.append(word)
            hash_hex = sha1(word.encode('utf-8')).hexdigest()
            hash_bin = bin(int(hash_hex, hex_scale))
            ini_hashes.append(hash_bin[2:])
        # add or subtract weights to value
        for i in range(len(ini_hashes)):
            for j in range(num_bits):
                if ini_hashes[i] == '0':
                    vector_values[j] -= page_content[page_words[i]]
                else:
                    vector_values[j] += page_content[page_words[i]]
        # build new fingerprint
        fingerprint = b''
        for value in vector_values:
            if value >= 0:
                fingerprint += b'1'
            else:
                fingerprint += b'0'
        return int(fingerprint, 2)

    def calculate_similarity(self, new_hash):
        # calculate the similarity of each page from the previous fingerprints
        similarity = 0
        for fingerprint in self.fingerprints:
            similarity = max(similarity, min(new_hash, fingerprint) / max(new_hash, fingerprint))
            if similarity > 0.85:
                return similarity
        return similarity

    def save_fingerprint(self, fingerprint):
        self.fingerprints.append(fingerprint)
