from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode
import os

# Function to generate RSA keys
def generate_keys(private_key_path, public_key_path):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Write private key to file
    with open(private_key_path, "wb") as private_key_file:
        private_key_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Write public key to file
    with open(public_key_path, "wb") as public_key_file:
        public_key_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

# Function to ensure keys exist
def ensure_keys_exist(private_key_path, public_key_path):
    if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
        generate_keys(private_key_path, public_key_path)

# Function to load private key from file
def load_private_key(file_path):
    with open(file_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

# Function to load public key from file
def load_public_key(file_path):
    with open(file_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key

# Function to encrypt a message using a public key
def encrypt_message(message, public_key):
    aes_key = os.urandom(32)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(message.encode()) + encryptor.finalize()

    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=SHA256()),
            algorithm=SHA256(),
            label=None
        )
    )

    return b64encode(iv + encrypted_key + encrypted_message).decode()

# Function to decrypt a message using a private key
def decrypt_message(encrypted_message, private_key):
    decoded_data = b64decode(encrypted_message.encode())
    iv = decoded_data[:16]
    encrypted_key = decoded_data[16:272]  # Adjusted to 272 to match the 2048-bit RSA key size
    encrypted_message = decoded_data[272:]

    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=SHA256()),
            algorithm=SHA256(),
            label=None
        )
    )

    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()

    return decrypted_message.decode()
