import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import stun_get_public_mapping, udp_hole_punch


class TestNatTraversal(unittest.IsolatedAsyncioTestCase):
    def test_stun_discovery(self):
        # Query public Google STUN server
        mapping = stun_get_public_mapping(stun_host="stun.l.google.com", timeout=3.0)
        self.assertIsNotNone(mapping, "STUN mapping failed to resolve")
        pub_ip, pub_port, loc_port = mapping
        self.assertTrue(len(pub_ip.split(".")) == 4, f"Invalid IP format: {pub_ip}")
        self.assertTrue(1 <= pub_port <= 65535)
        self.assertTrue(1 <= loc_port <= 65535)

    async def test_udp_hole_punch_loopback(self):
        # Test simulated direct UDP punch on loopback
        import socket

        target_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        target_sock.bind(("127.0.0.1", 19999))
        target_sock.setblocking(False)

        async def responder():
            loop = asyncio.get_running_loop()
            for _ in range(10):
                await asyncio.sleep(0.1)
                try:
                    data, addr = target_sock.recvfrom(1024)
                    target_sock.sendto(b"P2P_ACK:CONNECTED", addr)
                    break
                except BlockingIOError:
                    pass

        resp_task = asyncio.create_task(responder())
        ok = await udp_hole_punch(local_port=19998, peer_ip="127.0.0.1", peer_port=19999)
        await resp_task
        target_sock.close()
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
