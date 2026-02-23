#!/usr/bin/env python3
import argparse
import json
import random
import ipaddress
from http import HTTPStatus

def ipv4_subnet_calculator(ip_cidr):
    try:
        net = ipaddress.IPv4Network(ip_cidr, strict=False)
        return {
            "network_address": str(net.network_address),
            "broadcast_address": str(net.broadcast_address),
            "netmask": str(net.netmask),
            "hostmask": str(net.hostmask),
            "num_hosts": net.num_addresses - 2 if net.num_addresses > 2 else net.num_addresses,
            "min_host": str(net[1]) if net.num_addresses > 2 else str(net.network_address),
            "max_host": str(net[-2]) if net.num_addresses > 2 else str(net.broadcast_address)
        }
    except Exception as e:
        return {"error": str(e)}

def mac_address_generator(prefix=None):
    mac = [ 0x00, 0x16, 0x3e,
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff) ]
    if prefix:
        parts = prefix.split(':')
        for i, p in enumerate(parts):
            if i < 6:
                mac[i] = int(p, 16)
    
    return {"mac": ':'.join(map(lambda x: "%02x" % x, mac))}

def http_status_info(code):
    try:
        status = HTTPStatus(int(code))
        return {
            "code": status.value,
            "phrase": status.phrase,
            "description": status.description
        }
    except ValueError:
        return {"error": "Invalid HTTP status code"}

def main():
    parser = argparse.ArgumentParser(description="Network Tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subnet = subparsers.add_parser("subnet")
    subnet.add_argument("--cidr", required=True, help="e.g. 192.168.1.0/24")

    mac = subparsers.add_parser("mac")
    mac.add_argument("--prefix", help="e.g. 00:1A:2B")

    http = subparsers.add_parser("http-status")
    http.add_argument("--code", type=int, required=True)

    args = parser.parse_args()
    result = {}

    if args.command == "subnet":
        result = ipv4_subnet_calculator(args.cidr)
    elif args.command == "mac":
        result = mac_address_generator(args.prefix)
    elif args.command == "http-status":
        result = http_status_info(args.code)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
