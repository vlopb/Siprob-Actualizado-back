from django.contrib.auth.hashers import BasePasswordHasher
import os
from dotenv import load_dotenv


class XorPasswordHasher(BasePasswordHasher):
    algorithm = 'xor'

    def salt(self):
        return 'custom_salt'  # Custom salt for XOR

    def encode(self, password, salt):
        hash_input = f"{password}${salt}".encode('utf-8')
        key = os.getenv("APP_HASH_KEY")  # Custom key for XOR
        key_bytes = key.encode('utf-8')  # Convert key to bytes
        hashed = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(hash_input))
        return f"{self.algorithm}${hashed.hex()}"

    def verify(self, password, encoded):
        algorithm, hashed = encoded.split('$', 1)
        key = os.getenv("APP_HASH_KEY")  # Custom key for XOR
        key_bytes = key.encode('utf-8')  # Convert key to bytes
        hash_input = bytes(int(hashed[i:i+2], 16) ^ key_bytes[i % len(key_bytes)] for i in range(0, len(hashed), 2))
        return password == hash_input.decode('utf-8')


