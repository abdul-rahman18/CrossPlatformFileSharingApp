import socket
import os

# Client configuration
SERVER_HOST = '172.20.10.5'  # Change to the server's IP if on different machines
SERVER_PORT = 5001
BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"

def list_files(client_socket):
    client_socket.sendall("LIST".encode())
    response = client_socket.recv(4096).decode()
    if response == "NO_FILES":
        print("No files available on the server.")
    else:
        print("Files on server:")
        print(response)

def upload_file(client_socket):
    filepath = input("Enter the path of the file to upload: ")
    if not os.path.exists(filepath):
        print("File does not exist.")
        return
    filename = os.path.basename(filepath)
    client_socket.sendall(f"UPLOAD {filename}".encode())
    ready_response = client_socket.recv(BUFFER_SIZE).decode()
    if ready_response == "READY":
        with open(filepath, 'rb') as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)
        client_socket.sendall("END".encode())  # Signal end of file upload
        response = client_socket.recv(BUFFER_SIZE).decode()
        print(response)
    else:
        print("Server is not ready to receive the file.")

def download_file(client_socket):
    filename = input("Enter the filename to download: ")
    client_socket.sendall(f"DOWNLOAD {filename}".encode())
    status = client_socket.recv(BUFFER_SIZE).decode()
    
    if status == "EXISTS":
        client_socket.sendall("READY".encode())  # Confirm ready to receive file
        filepath = os.path.join("downloads", filename)
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
            
        with open(filepath, 'wb') as f:
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if bytes_read == b"END":
                    print(f"Download of {filename} completed successfully.")
                    break
                f.write(bytes_read)
    elif status == "NOT_FOUND":
        print("File does not exist on server.")
    else:
        print("Error:", status)

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
    except ConnectionRefusedError:
        print("Failed to connect to the server.")
        return

    print("Connected to the server.")

    while True:
        print("\nOptions:")
        print("1. List files")
        print("2. Upload file")
        print("3. Download file")
        print("4. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            list_files(client_socket)
        elif choice == '2':
            upload_file(client_socket)
        elif choice == '3':
            download_file(client_socket)
        elif choice == '4':
            client_socket.sendall("EXIT".encode())
            print("Disconnected from server.")
            break
        else:
            print("Invalid choice.")

    client_socket.close()

if __name__ == "__main__":
    main()
