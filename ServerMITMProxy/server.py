import cv2
import socket
import numpy as np
import pickle
import struct
import time
import threading

# Глобальная переменная для контроля основного цикла работы сервера
running = True

# Функция для обработки ввода команд от пользователя
def handle_input(video_control):
    global running
    while running:
        command = input("Введите команду (change, resume, stop): ")
        if command.startswith("change"):
            _, image_path = command.split()
            video_control["show_image"] = True
            video_control["image_path"] = image_path
            video_control["image"] = None  # Сброс текущего изображения
        elif command == "resume":
            video_control["show_image"] = False
        elif command == "stop":
            video_control["show_image"] = False
            running = False  # Завершение цикла работы сервера

# Главная функция сервера
def main():
    global running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = '192.168.158.1'  # Адрес сервера
    port = 4444               # Порт сервера
    server_socket.bind((host_ip, port))
    server_socket.listen(5)
    print("Ожидание подключения клиента на", (host_ip, port))

    client_socket, addr = server_socket.accept()
    print('Подключение клиента:', addr)

    droidcam_url = "http://172.28.105.121:4747/video"  # URL камеры DroidCam
    cap = cv2.VideoCapture()

    # Словарь для контроля отображения изображения
    video_control = {"show_image": False, "image_path": None, "image": None}
    threading.Thread(target=handle_input, args=(video_control,)).start()

    # Основной цикл сервера
    while running:
        # Пытаемся открыть поток DroidCam
        if not cap.open(droidcam_url):
            print("Не удаётся подключиться к DroidCam, попытка через 5 секунд...")
            time.sleep(5)
            continue

        while running:
            try:
                ret, frame = cap.read()
                if not ret:
                    break

                # Если нужно показать изображение, заменяем кадр из видеопотока
                if video_control["show_image"]:
                    if video_control["image_path"] and video_control["image"] is None:
                        video_control["image"] = cv2.imread(video_control["image_path"])
                        video_control["image"] = cv2.resize(video_control["image"], (frame.shape[1], frame.shape[0]))

                    frame = video_control["image"]

                # Отправляем кадр клиенту
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)
            except (BrokenPipeError, ConnectionResetError):
                # Переподключение при потере соединения
                print("Соединение потеряно, пытаюсь переподключиться...")
                client_socket, addr = server_socket.accept()
                print('Подключение клиента:', addr)
                time.sleep(30)

    # Закрытие всех соединений и освобождение ресурсов
    cap.release()
    client_socket.close()
    server_socket.close()
    print("Сервер завершил работу.")

if __name__ == "__main__":
    main()
