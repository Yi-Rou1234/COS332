import os
import hashlib
import socket
import time
import logging

# Configure logging
logging.basicConfig(filename='monitoring.log', level=logging.INFO)

def monitor_file(file_path, server_file_path, ftp_host, ftp_port, ftp_user, ftp_pass):
    # Get the initial hash of the file
    initial_hash = hash_file(file_path)

    while True:
        # Check if the file exists
        if not os.path.exists(file_path):
            logging.info(f"File '{file_path}' does not exist.")
            download_file(ftp_host, ftp_port, ftp_user, ftp_pass, server_file_path, file_path)
            initial_hash = hash_file(file_path)
        else:
            # Check if the file has been modified
            current_hash = hash_file(file_path)
            if current_hash != initial_hash:
                logging.info(f"File '{file_path}' has been modified.")
                download_file(ftp_host, ftp_port, ftp_user, ftp_pass, server_file_path, file_path)
                initial_hash = current_hash
        
        time.sleep(60)  # Poll every minute

def hash_file(file_path):
    # Compute the hash of the file
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def download_file(ftp_host, ftp_port, ftp_user, ftp_pass, server_file_path, local_file_path):
    # Connect to the FTP server and download the file
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ftp_socket:
            ftp_socket.connect((ftp_host, ftp_port))
            ftp_socket.recv(1024)  # Receive initial response
            ftp_socket.sendall(f"USER {ftp_user}\r\n".encode())
            ftp_socket.recv(1024)
            ftp_socket.sendall(f"PASS {ftp_pass}\r\n".encode())
            ftp_socket.recv(1024)
            ftp_socket.sendall(f"RETR {server_file_path}\r\n".encode())
            response = ftp_socket.recv(1024)
            with open(local_file_path, 'wb') as f:
                while True:
                    data = ftp_socket.recv(1024)
                    if not data:
                        break
                    f.write(data)
        logging.info(f"Downloaded '{server_file_path}' from FTP server.")
    except Exception as e:
        logging.error(f"Failed to download '{server_file_path}' from FTP server: {str(e)}")

if __name__ == "__main__":
    # File paths and FTP credentials
    monitored_file = "/path/to/monitored/file.txt"
    server_file = "/path/to/known-good/file.txt"
    ftp_host = "ftp.example.com"
    ftp_port = 21
    ftp_user = "yi-rou"
    ftp_pass = "monica0713"

    # Start monitoring the file
    monitor_file(monitored_file, server_file, ftp_host, ftp_port, ftp_user, ftp_pass)
