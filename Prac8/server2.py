import socket
import os
import hashlib
import time

# Configuration
local_file_path = "file.txt"
server_file_path = "/path/to/file.txt"
ftp_server = "ftp.gnu.org"
ftp_port = 21
ftp_username = "username"
ftp_password = "password"

def send_command(sock, command):
    sock.sendall(command.encode() + b'\r\n')

def receive_response(sock):
    response = ""
    while True:
        data = sock.recv(4096).decode()
        response += data
        if data.endswith('\r\n'):
            break
    return response

def login(sock, username, password):
    send_command(sock, "USER " + username)
    receive_response(sock)
    send_command(sock, "PASS " + password)
    response = receive_response(sock)
    return response.startswith("230")

def download_file(sock):
    send_command(sock, "RETR " + server_file_path)
    response = receive_response(sock)
    if response.startswith("150"):
        with open(local_file_path, 'wb') as f:
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                f.write(data)
        receive_response(sock)

def calculate_hash(file_path):
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

def monitor_file():
    original_hash = calculate_hash(local_file_path)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ftp_server, ftp_port))
        if login(sock, ftp_username, ftp_password):
            while True:
                current_hash = calculate_hash(local_file_path)
                if current_hash != original_hash:
                    print("File has been modified. Restoring original.")
                    download_file(sock)
                    original_hash = calculate_hash(local_file_path)
                time.sleep(60)  # Polling interval
        else:
            print("Login failed.")

if __name__ == "__main__":
    monitor_file()
