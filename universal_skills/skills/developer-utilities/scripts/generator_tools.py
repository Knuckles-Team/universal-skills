#!/usr/bin/env python3
import argparse
import json
import uuid
import secrets
import string
import time
import base64
import os


def generate_uuid(version=4):
    if version == 1:
        return {"uuid": str(uuid.uuid1())}
    elif version == 4:
        return {"uuid": str(uuid.uuid4())}
    else:
        return {"error": "Unsupported UUID version"}


def generate_ulid():
    t = int(time.time() * 1000)
    chars = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    ulid = ""
    for _ in range(10):
        ulid = chars[t % 32] + ulid
        t //= 32
    for _ in range(16):
        ulid += secrets.choice(chars)
    return {"ulid": ulid.zfill(26)}


def generate_token(length=32, chars="alphanumeric"):
    charset = string.ascii_letters + string.digits
    if chars == "hex":
        charset = string.hexdigits.lower()
    elif chars == "base64":
        return {
            "token": base64.urlsafe_b64encode(os.urandom(length))
            .decode("utf-8")
            .rstrip("=")[:length]
        }

    token = "".join(secrets.choice(charset) for _ in range(length))
    return {"token": token}


def generate_otp():
    return {"otp": "".join(secrets.choice(string.digits) for _ in range(6))}


def generate_password(
    length=16, uppercase=True, lowercase=True, numbers=True, symbols=True
):
    charset = ""
    if uppercase:
        charset += string.ascii_uppercase
    if lowercase:
        charset += string.ascii_lowercase
    if numbers:
        charset += string.digits
    if symbols:
        charset += string.punctuation

    if not charset:
        return {"error": "At least one character set must be selected"}

    password = "".join(secrets.choice(charset) for _ in range(length))
    return {"password": password}


def lorem_ipsum(paragraphs=1):
    lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    return {"text": "\n\n".join([lorem] * paragraphs)}


def main():
    parser = argparse.ArgumentParser(description="Generator Tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # uuid
    uuid_parser = subparsers.add_parser("uuid", help="Generate UUID")
    uuid_parser.add_argument(
        "--version", type=int, default=4, help="UUID version (1 or 4)"
    )

    # ulid
    subparsers.add_parser("ulid", help="Generate ULID")

    # token
    token_parser = subparsers.add_parser("token", help="Generate secure token")
    token_parser.add_argument("--length", type=int, default=32)
    token_parser.add_argument(
        "--chars", choices=["alphanumeric", "hex", "base64"], default="alphanumeric"
    )

    # otp
    subparsers.add_parser("otp", help="Generate 6-digit OTP")

    # password
    pass_parser = subparsers.add_parser("password", help="Generate secure password")
    pass_parser.add_argument("--length", type=int, default=16)
    pass_parser.add_argument("--no-upper", action="store_true")
    pass_parser.add_argument("--no-lower", action="store_true")
    pass_parser.add_argument("--no-numbers", action="store_true")
    pass_parser.add_argument("--no-symbols", action="store_true")

    # lorem
    lorem_parser = subparsers.add_parser("lorem", help="Generate Lorem Ipsum")
    lorem_parser.add_argument("--paragraphs", type=int, default=1)

    args = parser.parse_args()

    result = {}
    if args.command == "uuid":
        result = generate_uuid(args.version)
    elif args.command == "ulid":
        result = generate_ulid()
    elif args.command == "token":
        result = generate_token(args.length, args.chars)
    elif args.command == "otp":
        result = generate_otp()
    elif args.command == "password":
        result = generate_password(
            length=args.length,
            uppercase=not args.no_upper,
            lowercase=not args.no_lower,
            numbers=not args.no_numbers,
            symbols=not args.no_symbols,
        )
    elif args.command == "lorem":
        result = lorem_ipsum(args.paragraphs)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
