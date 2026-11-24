import asyncio
import struct
from logging import getLogger

from app.adapters import adapter
from app.adapters.binary_protocol import BinaryProtocolParser

logger = getLogger(__name__)

READ_TIMEOUT = 30.0


async def read_packet(reader: asyncio.StreamReader) -> bytes:
    """Читает один пакет целиком: заголовок, затем тело по длине из заголовка."""
    header = await reader.readexactly(BinaryProtocolParser.HEADER_SIZE)
    _, body_len = struct.unpack(BinaryProtocolParser.HEADER_FMT, header)
    return header + await reader.readexactly(body_len)


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    logger.info(f"Processing request from TCP client {addr}")

    response = b""
    try:
        data = await asyncio.wait_for(read_packet(reader), timeout=READ_TIMEOUT)
        logger.info(f"Received TCP data from {addr}: {data!r}")
        result = await adapter.process_packet(data, "TCP")
        response = f"OK {result['saved_messages']}\n".encode()
    except TimeoutError:
        response = b"ERR timeout\n"
        logger.warning(f"Timeout for {addr}")
    except asyncio.IncompleteReadError:
        response = b"ERR incomplete packet\n"
        logger.warning(f"Incomplete packet from {addr}")
    except Exception as e:
        response = f"ERR {e}\n".encode()
        logger.exception(f"Error processing {addr}")

    logger.info(f"Sending response to {addr}: {response!r}")
    writer.write(response)
    await writer.drain()
    if writer.can_write_eof():
        writer.write_eof()
    writer.close()
    await writer.wait_closed()


async def run_tcp_server(host: str, port: int, stop_event: asyncio.Event):
    logger.info(f"Starting tcp server on host={host}, port={port}")

    server = await asyncio.start_server(handle_client, host, port)
    async with server:
        await stop_event.wait()
        server.close()
        await server.wait_closed()
