#!/usr/bin/env python3
"""
NATranslate (nat_traversal): Zero-config P2P UDP hole punching & STUN NAT traversal CLI.
Built autonomously by Yoshi.
"""

import argparse
import asyncio
import os
import socket
import struct
import sys
import time
from typing import Optional, Tuple

DEFAULT_STUN_SERVERS = [
    ("stun.l.google.com", 19302),
    ("stun1.l.google.com", 19302),
    ("stun.cloudflare.com", 3478),
]


def stun_get_public_mapping(
    local_port: int = 0, stun_host: str = "stun.l.google.com", stun_port: int = 19302, timeout: float = 3.0
) -> Optional[Tuple[str, int, int]]:
    """
    Performs RFC 5389 STUN Binding Request over UDP to discover external IP & mapped port.
    Returns (public_ip, public_port, local_bound_port).
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    sock.bind(("0.0.0.0", local_port))
    actual_local_port = sock.getsockname()[1]

    # STUN Header: Type (0x0001 = Binding Request), Length (0), Magic Cookie (0x2112A442), 12-byte Transaction ID
    magic_cookie = 0x2112A442
    trans_id = os.urandom(12)
    header = struct.pack("!HHI", 0x0001, 0x0000, magic_cookie) + trans_id

    try:
        dest_addr = (socket.gethostbyname(stun_host), stun_port)
        sock.sendto(header, dest_addr)
        resp, _ = sock.recvfrom(2048)

        if len(resp) < 20:
            return None

        msg_type, msg_len, recv_cookie = struct.unpack("!HHI", resp[:8])
        if msg_type != 0x0101 or recv_cookie != magic_cookie:  # Binding Response
            return None

        # Parse attributes
        offset = 20
        end = 20 + msg_len
        while offset + 4 <= end:
            attr_type, attr_len = struct.unpack("!HH", resp[offset : offset + 4])
            val = resp[offset + 4 : offset + 4 + attr_len]

            # XOR-MAPPED-ADDRESS (0x0020)
            if attr_type == 0x0020 and len(val) >= 8:
                family = val[1]
                x_port = struct.unpack("!H", val[2:4])[0]
                port = x_port ^ (magic_cookie >> 16)
                if family == 0x01:  # IPv4
                    x_ip = struct.unpack("!I", val[4:8])[0]
                    ip_int = x_ip ^ magic_cookie
                    ip = socket.inet_ntoa(struct.pack("!I", ip_int))
                    return (ip, port, actual_local_port)

            # MAPPED-ADDRESS (0x0001)
            elif attr_type == 0x0001 and len(val) >= 8:
                family = val[1]
                port = struct.unpack("!H", val[2:4])[0]
                if family == 0x01:  # IPv4
                    ip = socket.inet_ntoa(val[4:8])
                    return (ip, port, actual_local_port)

            offset += 4 + ((attr_len + 3) & ~3)

    except Exception:
        pass
    finally:
        sock.close()

    return None


async def udp_hole_punch(local_port: int, peer_ip: str, peer_port: int, message: str = "P2P_HELLO") -> bool:
    """
    Performs simultaneous UDP hole punching by sending sync probes to peer until hole is established.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    sock.bind(("0.0.0.0", local_port))
    loop = asyncio.get_running_loop()

    print(f"[*] Probing NAT hole from local UDP :{local_port} to {peer_ip}:{peer_port}...")
    success = False

    for attempt in range(10):
        probe_packet = f"HOLE_PUNCH:{attempt}:{message}".encode("utf-8")
        sock.sendto(probe_packet, (peer_ip, peer_port))
        await asyncio.sleep(0.3)

        # Check for response
        try:
            data, addr = sock.recvfrom(1024)
            if addr[0] == peer_ip or str(addr[1]) == str(peer_port):
                print(f"[+] NAT Hole punched! Direct P2P packet received from {addr}: {data.decode(errors='ignore')}")
                sock.sendto(b"P2P_ACK:CONNECTED", addr)
                success = True
                break
        except BlockingIOError:
            pass

    sock.close()
    return success


def main():
    parser = argparse.ArgumentParser(description="NATranslate: Zero-config P2P NAT Traversal & STUN Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # STUN discovery
    stun_p = subparsers.add_parser("stun", help="Discover public IP and NAT mapped port via STUN")
    stun_p.add_argument("--port", type=int, default=0, help="Local UDP port to bind (default: random ephemeral)")
    stun_p.add_argument("--server", default="stun.l.google.com", help="STUN server hostname")

    # UDP hole punch
    punch_p = subparsers.add_parser("punch", help="Punch UDP hole to remote peer")
    punch_p.add_argument("--local-port", type=int, required=True, help="Local bound port matching STUN mapping")
    punch_p.add_argument("--peer-ip", type=str, required=True, help="Remote peer external IP")
    punch_p.add_argument("--peer-port", type=int, required=True, help="Remote peer external port")
    punch_p.add_argument("--msg", default="P2P_ACTIVE", help="Message payload to send across link")

    # Echo listener
    echo_p = subparsers.add_parser("listen", help="Listen for incoming UDP P2P packets on a port")
    echo_p.add_argument("--port", type=int, required=True, help="Local port to listen on")

    args = parser.parse_args()

    if args.command == "stun":
        res = stun_get_public_mapping(local_port=args.port, stun_host=args.server)
        if res:
            pub_ip, pub_port, loc_port = res
            print(f"[+] STUN Discovery Successful:")
            print(f"    Public IP:        {pub_ip}")
            print(f"    External Port:    {pub_port}")
            print(f"    Local Bound Port: {loc_port}")
        else:
            print("[-] STUN request timed out or failed.")
            sys.exit(1)

    elif args.command == "punch":
        ok = asyncio.run(udp_hole_punch(args.local_port, args.peer_ip, args.peer_port, args.msg))
        sys.exit(0 if ok else 1)

    elif args.command == "listen":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", args.port))
        print(f"[*] Listening for UDP P2P packets on 0.0.0.0:{args.port}...")
        while True:
            data, addr = sock.recvfrom(2048)
            print(f"[<] Packet from {addr}: {data.decode(errors='ignore')}")
            sock.sendto(b"ACK:RECEIVED", addr)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()