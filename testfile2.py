import socket
import struct

from crcmod.predefined import mkCrcFun

# --- Константы из вашего парсера ---
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
    body += b"\xff"  # Маркер конца

    device_id = device_id_str.encode("utf-8").ljust(12, b"\x00")[:12]
    header = struct.pack(HEADER_FMT, device_id, len(body))
    return header + body


def main():
    # Данные для двух сообщений
    msg1 = (1, 12.2, 22.5, (12, 12, 12), (34, 34, 43), (45, 64, 32), 1.0, 30.0)
    msg2 = (2, 12.3, 22.6, (13, 13, 13), (35, 35, 44), (46, 65, 33), 2.0, 31.0)

    # Генерируем бинарный пакет
    packet = build_packet("TEST_DEVICE_UDP", [msg1, msg2])
    print(f"Сгенерирован UDP-пакет размером {len(packet)} байт")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3.0)

    try:
        print("Отправляем UDP пакет на localhost:9998...")
        sock.sendto(packet, ("localhost", 9998))

        # Ждём ответ
        data, addr = sock.recvfrom(1024)
        print(f"✅ Получен UDP ответ: {data.decode('utf-8', errors='replace').strip()}")

    except ConnectionResetError:
        print("Ошибка 10054: Сервер не ответил (порт закрыт или контейнер не запущен).")
    except TimeoutError:
        print("Таймаут: Сервер не прислал ответ за 3 секунды.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
