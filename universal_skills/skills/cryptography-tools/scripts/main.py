#!/usr/bin/env python3
import argparse
import hashlib
import hmac
import base64
import json

try:
    import bcrypt
except ImportError:
    bcrypt = None

try:
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
except ImportError:
    rsa = None


def hash_bcrypt(password, rounds=12):
    if bcrypt is None:
        return {"error": "bcrypt library is not installed."}
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return {"hash": hashed.decode("utf-8")}


def check_bcrypt(password, hashed):
    if bcrypt is None:
        return {"error": "bcrypt library is not installed."}
    is_match = bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    return {"match": is_match}


def hash_text(text, algorithm="sha256"):
    try:
        m = hashlib.new(algorithm)
        m.update(text.encode("utf-8"))
        return {"hash": m.hexdigest(), "algorithm": algorithm}
    except ValueError as e:
        return {"error": str(e)}


def generate_hmac(key, message, algorithm="sha256"):
    try:
        h = hmac.new(
            key.encode("utf-8"), message.encode("utf-8"), getattr(hashlib, algorithm)
        )
        return {"hmac": h.hexdigest(), "algorithm": algorithm}
    except Exception as e:
        return {"error": str(e)}


def generate_rsa_keypair(key_size=2048):
    if rsa is None:
        return {"error": "cryptography library is not installed."}
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    unencrypted_pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return {
        "private_key": unencrypted_pem_private_key.decode("utf-8"),
        "public_key": pem_public_key.decode("utf-8"),
    }


def string_obfuscator(text):
    b64 = base64.b64encode(text.encode("utf-8")).decode("utf-8")
    hex_encoded = b64.encode("utf-8").hex()
    return {"obfuscated": hex_encoded}


def main():
    parser = argparse.ArgumentParser(description="Crypto Tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # bcrypt
    bcrypt_parser = subparsers.add_parser("bcrypt", help="Bcrypt password hashing")
    bcrypt_parser.add_argument("--password", required=True, help="Password to hash")
    bcrypt_parser.add_argument("--rounds", type=int, default=12, help="Log rounds")
    bcrypt_parser.add_argument("--check", help="Hash to check against")

    # hash-text
    hash_parser = subparsers.add_parser(
        "hash-text", help="Hash text (md5, sha1, sha256, etc)"
    )
    hash_parser.add_argument("--text", required=True, help="Text to hash")
    hash_parser.add_argument(
        "--algorithm", default="sha256", help="Algorithm (sha256, md5, etc)"
    )

    # hmac-generator
    hmac_parser = subparsers.add_parser("hmac-generator", help="Generate HMAC")
    hmac_parser.add_argument("--key", required=True, help="Secret key")
    hmac_parser.add_argument("--message", required=True, help="Message")
    hmac_parser.add_argument("--algorithm", default="sha256", help="Algorithm")

    # rsa-key-pair-generator
    rsa_parser = subparsers.add_parser(
        "rsa-key-pair-generator", help="Generate RSA Key Pair"
    )
    rsa_parser.add_argument(
        "--size", type=int, default=2048, help="Key size (e.g. 2048, 4096)"
    )

    # string-obfuscator
    obf_parser = subparsers.add_parser("string-obfuscator", help="Obfuscate a string")
    obf_parser.add_argument("--text", required=True, help="Text to obfuscate")

    args = parser.parse_args()

    result = {}
    if args.command == "bcrypt":
        if args.check:
            result = check_bcrypt(args.password, args.check)
        else:
            result = hash_bcrypt(args.password, args.rounds)
    elif args.command == "hash-text":
        result = hash_text(args.text, args.algorithm)
    elif args.command == "hmac-generator":
        result = generate_hmac(args.key, args.message, args.algorithm)
    elif args.command == "rsa-key-pair-generator":
        result = generate_rsa_keypair(args.size)
    elif args.command == "string-obfuscator":
        result = string_obfuscator(args.text)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
