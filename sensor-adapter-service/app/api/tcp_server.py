import asyncio
from logging import getLogger
from app.adapters import adapter

logger = getLogger(__name__)


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    logger.info(f"Processing request from TCP client {addr}")

    response = b""
    try:
        data = await asyncio.wait_for(reader.read(65536), timeout=5.0)
        logger.info(f"Received TCP data from {addr}: {data!r}")
        result = await adapter.process_packet(data, "TCP")
        response = f"OK {result['saved_messages']}\n".encode()
    except asyncio.TimeoutError:
        response = b"ERR timeout\n"
        logger.warning(f"Timeout for {addr}")
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
