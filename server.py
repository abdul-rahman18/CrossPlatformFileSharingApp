import socket
import threading
import os

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5001
BUFFER_SIZE = 1024
FILES_DIRECTORY = 'shared_files'

# Ensure the shared files directory exists
if not os.path.exists(FILES_DIRECTORY):
    os.makedirs(FILES_DIRECTORY)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    while True:
        try:
            # Receive command from client
            command = conn.recv(BUFFER_SIZE).decode()
            if not command:
                break
            print(f"[COMMAND] {command} from {addr}")

            if command == "LIST":
                files = os.listdir(FILES_DIRECTORY)
                if not files:
                    conn.sendall("NO_FILES".encode())
                else:
                    files_list = "\n".join(files)
                    conn.sendall(files_list.encode())

            elif command.startswith("UPLOAD"):
                filename = command.split(maxsplit=1)[1]
                filepath = os.path.join(FILES_DIRECTORY, filename)
                conn.sendall("READY".encode())  # Signal ready to receive file
                with open(filepath, 'wb') as f:
                    while True:
                        bytes_read = conn.recv(BUFFER_SIZE)
                        if bytes_read == b"END":
                            print(f"Upload of {filename} completed.")
                            break
                        f.write(bytes_read)
                conn.sendall(f"Upload of {filename} successful.".encode())

            elif command.startswith("DOWNLOAD"):
                filename = command.split(maxsplit=1)[1]
                filepath = os.path.join(FILES_DIRECTORY, filename)
                
                if os.path.exists(filepath):
                    conn.sendall("EXISTS".encode())
                    client_ready = conn.recv(BUFFER_SIZE).decode()
                    
                    if client_ready == "READY":
                        with open(filepath, 'rb') as f:
                            while True:
                                bytes_read = f.read(BUFFER_SIZE)
                                if not bytes_read:
                                    break
                                conn.sendall(bytes_read)
                        conn.sendall(b"END")  # Send an "END" signal after the file is sent
                        print(f"Download of {filename} completed for {addr}.")
                else:
                    conn.sendall("NOT_FOUND".encode())

            elif command == "EXIT":
                print(f"[DISCONNECT] {addr} disconnected.")
                break

            else:
                conn.sendall("INVALID COMMAND".encode())

        except ConnectionResetError:
            print(f"[DISCONNECT] {addr} disconnected abruptly.")
            break

    conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() -1}")

if __name__ == "__main__":
    start_server()
