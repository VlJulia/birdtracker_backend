import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(3.0)  # Важно: ставим таймаут, чтобы не ждать вечно
try:
    # Отправляем пакет
    sock.sendto(b"test_packet", ("localhost", 9998))
    print("Пакет UDP отправлен, ждём ответ...")

    # Пытаемся получить ответ
    data, addr = sock.recvfrom(1024)
    print(f"Получен UDP ответ: {data} от {addr}")

except ConnectionResetError:
    print("Ошибка 10054: Сервер не ответил (порт закрыт или контейнер не запущен).")
except TimeoutError:
    print("Таймаут: Сервер не прислал ответ за 3 секунды.")
finally:
    sock.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #
sock.settimeout(3.0)  # Важно: ставим таймаут, чтобы не ждать вечно

try:
    print("Подключаемся к TCP-серверу...")
    # 2. Устанавливаем соединение
    sock.connect(("localhost", 9999))
    print("Соединение установлено, отправляем пакет...")

    # 3. Отправляем данные
    sock.sendall(b"test_packet")
    sock.shutdown(socket.SHUT_WR)  # тут мы заканчиваем

    # 4. Получаем ответ
    data = sock.recv(1024)
    print(f"Получен ответ: {data}")

except ConnectionRefusedError:
    print("Ошибка: Сервер не запущен или порт закрыт.")
except TimeoutError:
    print("Таймаут: Сервер не ответил за 3 секунды.")
except Exception as e:
    print(f"Произошла ошибка: {e}")
finally:
    # 5. Закрываем соединение
    sock.close()
