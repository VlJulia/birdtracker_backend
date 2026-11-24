import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from app.api.tcp_server import handle_client
from tests.message_generator import MessageGenerator


def build_packet() -> bytes:
    body = (
        MessageGenerator()
        .with_message_0x02(12, 12.2, 22.5, [1, 2, 3], [4, 5, 6], [7, 8, 9], 1.0, 30.0)
        .get_buffer()
    )
    header = MessageGenerator().with_header(b"F" * 12, len(body)).get_buffer()
    return header + body


class TestTcpServer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.process_packet = AsyncMock(return_value={"saved_messages": 1})
        patcher = patch(
            "app.api.tcp_server.adapter.process_packet", self.process_packet
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        self.server = await asyncio.start_server(handle_client, "127.0.0.1", 0)
        self.port = self.server.sockets[0].getsockname()[1]

    async def asyncTearDown(self):
        self.server.close()
        await self.server.wait_closed()

    async def send(self, *chunks: bytes) -> bytes:
        reader, writer = await asyncio.open_connection("127.0.0.1", self.port)
        for chunk in chunks:
            writer.write(chunk)
            await writer.drain()
            await asyncio.sleep(0.05)
        writer.write_eof()
        response = await reader.read()
        writer.close()
        await writer.wait_closed()
        return response

    async def test_packet_sent_in_chunks_is_read_whole(self):
        packet = build_packet()

        response = await self.send(packet[:5], packet[5:20], packet[20:])

        self.assertEqual(response, b"OK 1\n")
        self.process_packet.assert_awaited_once_with(packet, "TCP")

    async def test_incomplete_packet_is_rejected(self):
        packet = build_packet()

        response = await self.send(packet[:-1])

        self.assertEqual(response, b"ERR incomplete packet\n")
        self.process_packet.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
