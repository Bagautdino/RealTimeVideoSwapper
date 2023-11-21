import cv2
import socket
import numpy as np
import pickle
import struct
import time

def main():
    host_ip = '192.168.158.1'  # Адрес сервера
    port = 4444               # Порт сервера
    payload_size = struct.calcsize("Q")  # Размер заголовка сообщения

    while True:
        # Создание сокета с контекстным менеджером для автоматического закрытия
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                # Попытка подключения к серверу
                print("Попытка подключения к серверу...")
                client_socket.connect((host_ip, port))
                print("Соединение установлено")
                data = b""  # Буфер для хранения полученных данных

                while True:
                    # Получение данных до достижения размера заголовка
                    while len(data) < payload_size:
                        packet = client_socket.recv(4*1024)  # Получение пакета данных
                        if not packet: 
                            raise socket.error("Соединение прервано")
                        data += packet

                    # Извлечение размера сообщения из заголовка
                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    msg_size = struct.unpack("Q", packed_msg_size)[0]

                    # Получение всего сообщения на основе его размера
                    while len(data) < msg_size:
                        data += client_socket.recv(4*1024)
                    frame_data = data[:msg_size]
                    data = data[msg_size:]

                    # Десериализация данных и отображение кадра
                    frame = pickle.loads(frame_data)
                    cv2.imshow("Received", frame)  # Отображение полученного кадра
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break  # Выход из цикла по нажатию клавиши 'q'
            except (ConnectionRefusedError, socket.error):
                # Обработка исключений при потере соединения
                print("Соединение прервано, повторная попытка через 1 секунду...")
                time.sleep(1)  # Ожидание перед повторной попыткой подключения
                continue

if __name__ == "__main__":
    main()
