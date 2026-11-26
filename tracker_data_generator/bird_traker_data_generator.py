import argparse
import hashlib
import hmac
import os
import random
import socket
import struct
import time
from pathlib import Path

from faker import Faker
from faker.providers import BaseProvider


def load_env_file(name=".env"):
    path = Path(__file__).resolve().parent / name
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


load_env_file()

PROTOCOL_VERSION = 1
DEVICE_ID = b"\x01\x02\x03\x04"

IP = os.environ.get("SERVER_IP", "127.0.0.1")
SECRET_KEY = os.environ.get("SECRET_KEY", "").encode()


def get_default_port():
    value = os.environ.get("SERVER_PORT", "").strip() or "9000"
    try:
        return int(value)
    except ValueError:
        raise SystemExit(f"SERVER_PORT должен быть числом, а там: {value}")


class Tracker(BaseProvider):
    def health(self, rtc):
        # 9 байт: тип, rtc, батарея, солнце
        return struct.pack(
            "<BIHH", 0x01, rtc, self.random_int(3300, 4200), self.random_int(0, 6000)
        )

    def main_data(self, rtc):
        # 37 байт: тип, rtc, lat, lon, acc(3), gyro(3), mag(3), temp, батарея, солнце
        lat = self.random_int(562000000, 564000000)  # 1e-7 градуса, около Нижнего Новгорода
        lon = self.random_int(438000000, 441000000)
        acc = [self.random_int(-2000, 2000) for _ in range(3)]
        gyro = [self.random_int(-500, 500) for _ in range(3)]
        mag = [self.random_int(-1000, 1000) for _ in range(3)]
        temp = self.random_int(-1500, 3500)  # сотые доли градуса
        return struct.pack(
            "<BIii9hhHH",
            0x02,
            rtc,
            lat,
            lon,
            *acc,
            *gyro,
            *mag,
            temp,
            self.random_int(3300, 4200),
            self.random_int(0, 6000),
        )

    def time_sync(self, rtc):
        # 10 байт: тип, rtc, сдвиг UTC-RTC, источник (0 - GNSS, 1 - сеть)
        offset = int(time.time()) - rtc
        return struct.pack("<BIiB", 0x03, rtc, offset, self.random_element((0, 1)))


fake = Faker()
fake.add_provider(Tracker)


def sign(data, key):
    # от хэша берём первые 4 байта
    return hmac.new(key, data, hashlib.sha256).digest()[:4]


def build_data_packet(session_key, msg_number, first_id, records, is_last=False):
    # шапка потока: stream_id (0 - лог измерений), номер первой записи, количество
    payload = struct.pack("<BIB", 0, first_id, len(records)) + b"".join(records)

    header = struct.pack(
        "<BBB4sHHH",
        PROTOCOL_VERSION,
        0x01,
        0x01 if is_last else 0x00,
        DEVICE_ID,
        session_key,
        msg_number,
        len(payload),
    )
    body = header + payload
    return body + sign(body, SECRET_KEY)


def parse_ack(raw, session_key, msg_number):
    # в ответе минимум: 13 байт заголовка, 5 байт нагрузки, 4 байта подписи
    if len(raw) < 22:
        print("ACK битый: слишком короткий")
        return None

    body, signature = raw[:-4], raw[-4:]
    if sign(body, SECRET_KEY) != signature:
        print("ACK битый: подпись не сошлась")
        return None

    version, msg_type, flags, dev_id, resp_session, resp_number, payload_len = struct.unpack(
        "<BBB4sHHH", body[:13]
    )

    if msg_type != 0x02:
        print(f"ACK не тот тип: 0x{msg_type:02x}")
        return None
    if resp_session != session_key or resp_number != msg_number:
        print("ACK от другого сеанса или сообщения")
        return None

    payload = body[13 : 13 + payload_len]
    stream_id, count = struct.unpack("<BI", payload[:5])
    print(f"ACK: поток {stream_id}, принято {count}")
    return count


def parse_args():
    parser = argparse.ArgumentParser(
        description="Генератор UDP-пакетов трекера",
        epilog="Пример: python3 bird_traker_data_generator.py --type 2 --packets 10",
    )
    parser.add_argument("--ip", default=IP, help=f"адрес сервера (по умолчанию {IP})")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=get_default_port(),
        help="UDP-порт сервера",
    )
    parser.add_argument(
        "-t",
        "--type",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="1 - батарея и солнце, 2 - координаты и датчики, 3 - синхронизация времени",
    )
    parser.add_argument("-n", "--packets", type=int, default=5, help="сколько пакетов отправить")
    parser.add_argument("-r", "--records", type=int, default=3, help="записей в пакете")
    parser.add_argument("-d", "--delay", type=float, default=0.2, help="пауза между пакетами, с")
    return parser.parse_args()


def main():
    args = parse_args()

    if not SECRET_KEY:
        raise SystemExit("Нет SECRET_KEY. Добавь его в .env или в переменные окружения.")

    make_record = {1: fake.health, 2: fake.main_data, 3: fake.time_sync}[args.type]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    session_key = random.randint(1, 65535)
    rtc = 1000  # секунды от включения
    first_id = 1
    sent = 0

    print(f"сеанс {session_key}, шлю на {args.ip}:{args.port}, записей {args.records} в пакете")

    for number in range(1, args.packets + 1):
        last = number == args.packets
        records = [make_record(rtc + sent + i) for i in range(args.records)]
        packet = build_data_packet(session_key, number, first_id, records, last)
        sock.sendto(packet, (args.ip, args.port))
        print(f"пакет {number}/{args.packets}: {len(records)} записей, {len(packet)} байт")

        first_id += len(records)
        sent += len(records)

        if not last:
            time.sleep(args.delay)

    print("ждём ACK")
    try:
        raw, _ = sock.recvfrom(1024)
    except socket.timeout:
        print("сервер не ответил за 3 секунды")
        sock.close()
        return

    confirmed = parse_ack(raw, session_key, args.packets)
    if confirmed is not None:
        print(f"отправлено {sent}, подтверждено {confirmed}")

    sock.close()


if __name__ == "__main__":
    main()
