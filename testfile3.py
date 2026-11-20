import socket
import struct
from crcmod.predefined import mkCrcFun

HEADER_FMT = "<12sH"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
MSG_SENSOR_ALL_FMT = "<BIffhhhhhhhhhff"
MSG_SENSOR_ALL_SIZE = struct.calcsize(MSG_SENSOR_ALL_FMT)
CRC_FMT = "<B"
CRC_SIZE = struct.calcsize(CRC_FMT)
CRC8_FUNC = mkCrcFun("crc-8-maxim")


def build_sensor_message(timestamp, lat, lon, acc, gyr, mag, light, temp):
    packed_body = struct.pack(
        MSG_SENSOR_ALL_FMT,
        0x02,
        timestamp,
        lat,
        lon,
        acc[0],
        acc[1],
        acc[2],
        gyr[0],
        gyr[1],
        gyr[2],
        mag[0],
        mag[1],
        mag[2],
        light,
        temp,
    )
    crc = CRC8_FUNC(packed_body)
    return packed_body + struct.pack(CRC_FMT, crc)


def build_packet(device_id_str, messages_data):
    body = b""
    for msg in messages_data:
        body += build_sensor_message(*msg)
    body += b"\xff"
    device_id = device_id_str.encode("utf-8").ljust(12, b"\x00")[:12]
    header = struct.pack(HEADER_FMT, device_id, len(body))
    return header + body


def main():
    msg1 = (1, 12.2, 22.5, (12, 12, 12), (34, 34, 43), (45, 64, 32), 1.0, 30.0)
    msg2 = (2, 12.3, 22.6, (13, 13, 13), (35, 35, 44), (46, 65, 33), 2.0, 31.0)
    packet = build_packet("TEST_DEVICE_1", [msg1, msg2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 1. Включаем TCP_NODELAY (отключаем алгоритм Нейгла, чтобы данные не задерживались)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.settimeout(5.0)

    try:
        print("Подключаемся к TCP-серверу localhost:9999...")
        sock.connect(("localhost", 9999))

        print("Отправляем пакет...")
        sock.sendall(packet)

        # ⚠️ ВАЖНО: Сообщаем серверу, что мы закончили отправку (шлём FIN)
        sock.shutdown(socket.SHUT_WR)

        print("Ожидаем ответ...")

        # 2. Читаем в цикле, чтобы поймать данные, даже если они придут частями
        chunks = []
        while True:
            try:
                chunk = sock.recv(1024)
                if not chunk:
                    # Если пришёл пустой байт — значит, сервер закрыл соединение
                    break
                chunks.append(chunk)
                # Если получили ответ (например, заканчивается на \n), можно прервать цикл
                if b"\n" in chunk:
                    break
            except socket.timeout:
                print("Таймаут при чтении.")
                break

        response = b"".join(chunks)

        if not response:
            print(
                "❌ Сервер закрыл соединение, не отправив данных (или произошёл RST от Windows)."
            )
        else:
            print(f"✅ Ответ сервера: {response.decode('utf-8', errors='replace')}")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
