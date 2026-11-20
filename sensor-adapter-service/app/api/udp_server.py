import asyncio
from logging import getLogger
from app.adapters import adapter

logger = getLogger(__name__)


class UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, stop_event: asyncio.Event):
        self.stop_event = stop_event
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        logger.info(f"UDP server started on {transport.get_extra_info('sockname')}")

    def datagram_received(self, data: bytes, addr):
        asyncio.create_task(self._process(data, addr))

    async def _process(self, data: bytes, addr):
        logger.info(f"Processing request from UDP client {addr}")
        response = b""

        try:
            result = await adapter.process_packet(data, "UDP")
            response = f"OK {result['saved_messages']}\n".encode()
        except Exception as e:
            logger.exception(f"Error processing UDP packet from {addr}")
            response = f"ERR {e}\n".encode()

        self.transport.sendto(response, addr)
        logger.info(f"UDP client {addr} processed")

    def error_received(self, exc):
        logger.error(f"UDP error: {exc}")

    def connection_lost(self, exc):
        logger.info("UDP server closed")


async def run_udp_server(host: str, port: int, stop_event: asyncio.Event):
    logger.info(f"Starting udp server on host={host}, port={port}")
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPProtocol(stop_event),
        local_addr=(host, port),
    )

    try:
        await stop_event.wait()
    finally:
        transport.close()
        logger.info("UDP server stopped")
