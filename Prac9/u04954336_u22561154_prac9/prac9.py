#!/usr/bin/python3
import socket
import threading
import hashlib
import datetime

# Define the proxy server and real POP3 server details
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 55555
REAL_POP3_HOST = 'localhost'
REAL_POP3_PORT = 110
REAL_USERNAME = 'lloyd'
REAL_PASSWORD = 'testpassword'

# Function to handle client connection
def handle_client(client_socket):
    try:
        client_socket.send(b'+OK Proxy POP3 server ready\r\n')
        authenticated = False
        admin = False
        
        # User authentication process
        while not authenticated:
            data = client_socket.recv(1024).decode('utf-8').strip()
            if data.upper().startswith('USER'):
                username = data.split()[1]
                client_socket.send(b'+OK User accepted\r\n')
            elif data.upper().startswith('PASS'):
                password = data.split()[1]
                # Find the salt for the username
                salt = None
                with open('username-password.txt', 'r') as f:
                    for line in f:
                        if line.split()[0] == username:
                            salt = line.split()[2]
                            break
                # Hash the password with the salt
                if salt:
                    hash_object = hashlib.sha256()
                    hash_object.update(f'{password}{salt}'.encode('utf-8'))
                    hashed_password = hash_object.hexdigest()
                    # Check if the passwords match
                    with open('username-password.txt', 'r') as f:
                        for line in f:
                            if line.split()[0] == username and line.split()[1] == hashed_password:
                                authenticated = True
                                client_socket.send(b'+OK User successfully authenticated\r\n')
                                if line.split()[3] == 'admin':
                                    admin = True
                                    client_socket.send(b'+OK Logged in as admin\r\n')
                                else:
                                    client_socket.send(b'+OK Logged in as user\r\n')
                                break
                if not authenticated:
                    client_socket.send(b'-ERR Authentication failed\r\n')
                    client_socket.close()
                    return
            elif data.upper().startswith('QUIT'):
                #QUIT
                client_socket.send(b'+OK Goodbye\r\n')
                client_socket.close()
                return
            else:
                client_socket.send(b'-ERR Invalid command\r\n')
        
        # Log the login attempt
        if(authenticated):
            if(admin):
                log_message(f'Admin login attempt by {username} - SUCCESS', client_socket)
            else:
                log_message(f'User login attempt by {username} - SUCCESS', client_socket)
        else:
            log_message(f'Login attempt - FAILURE', client_socket)
            
        # If authenticated, connect to the real POP3 server
        if authenticated:
            real_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            real_server.connect((REAL_POP3_HOST, REAL_POP3_PORT))
            real_server.recv(1024)  # Read the server's greeting

            # Authenticate with the real server
            real_server.sendall(f'USER {REAL_USERNAME}\r\n'.encode('utf-8'))
            real_server.recv(1024)
            real_server.sendall(f'PASS {REAL_PASSWORD}\r\n'.encode('utf-8'))
            real_server.recv(1024)
            
            

            if not admin:
                #Create a LIST that RETR and LIST will respond to with confidential filtered out, if there is a non-admin user
                real_server.sendall(b'LIST\r\n')
                response = real_server.recv(4096)
                # Construct a new list excluding confidential messages
                new_list = []
                for line in response.decode('utf-8').split('\n')[1:]:
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            msg_num, _ = parts
                            real_server.sendall(f'RETR {msg_num}\r\n'.encode('utf-8'))
                            msgData = real_server.recv(1024).decode('utf-8')
                            if not filter_confidential(msgData):
                                new_list.append(line)
                #Construct a new list excluding confidential messages for UIDL
                new_list_uidl = []
                real_server.sendall(b'UIDL\r\n')
                response = real_server.recv(4096)
                for line in response.decode('utf-8').split('\n')[1:]:
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            msg_num, _ = parts
                            real_server.sendall(f'RETR {msg_num}\r\n'.encode('utf-8'))
                            msgData = real_server.recv(1024).decode('utf-8')
                            if not filter_confidential(msgData):
                                new_list_uidl.append(line)
                    
            

                
            
            
            while True:
                data = client_socket.recv(1024).decode('utf-8').strip()
                if data.upper().startswith('LIST'):
                    if not admin:
                        #Get how many messages are in the new list
                        #Build response with the new_list
                        response = f'+OK {len(new_list)} messages\r\n';
                        index = 1;
                        for line in new_list:
                            #Starting from 1, list the message number as the index
                            #Remove the message number from the line
                            response += f'{index} {line.split()[1]}\r\n'
                            index += 1
                        #Add a period to the end of the response
                        response += '.\r\n'
                        client_socket.send(response.encode('utf-8'))     
                        log_message(f'LIST - SUCCESSFUL', client_socket)                   
                    else:
                        real_server.sendall(b'LIST\r\n')
                        response = real_server.recv(4096)
                        client_socket.send(response)
                        #log
                        log_message(f'LIST - SUCCESSFUL', client_socket)
                elif data.upper().startswith('RETR'):
                    if not admin:
                        message_number = data.split()[1]
                        #Find the message in the new_list, via index
                        #Get the message number from the line
                        #Send the RETR command to the real server
                        #Send the message to the client
                        if(int(message_number) > len(new_list)):
                            response = f'-ERR There is no message {message_number}\r\n'
                            client_socket.send(response.encode('utf-8'))
                            #log
                            log_message(f'RETR - UNSUCCESSFUL', client_socket)
                        else:
                            msg_num = new_list[int(message_number) - 1].split()[0]
                            real_server.sendall(f'RETR {msg_num}\r\n'.encode('utf-8'))
                            response = real_server.recv(4096)
                            client_socket.send(response)
                            #log
                            log_message(f'RETR - SUCCESSFUL', client_socket)
                    else:
                        message_number = data.split()[1]
                        real_server.sendall(f'RETR {message_number}\r\n'.encode('utf-8'))
                        response = real_server.recv(4096)
                        client_socket.send(response)
                        #log
                        log_message(f'RETR - SUCCESSFUL', client_socket)
                elif data.upper().startswith('DELE') and admin:
                    message_number = data.split()[1]
                    real_server.sendall(f'DELE {message_number}\r\n'.encode('utf-8'))
                    response = real_server.recv(1024)
                    client_socket.send(response)
                    #log
                    log_message(f'DELE - SUCCESSFUL', client_socket)
                elif data.upper().startswith('DELE') and not admin:
                    client_socket.send(b'-ERR Only admin can delete messages\r\n')
                    #log
                    log_message(f'DELE - UNSUCCESSFUL', client_socket)
                elif data.upper().startswith('QUIT'):
                    real_server.sendall(b'QUIT\r\n')
                    real_server.recv(1024)
                    client_socket.send(b'+OK Goodbye\r\n')
                    #log
                    log_message(f'QUIT - SUCCESSFUL', client_socket)
                    client_socket.close()
                    break
                elif data.upper().startswith('STAT'):
                    real_server.sendall(b'STAT\r\n')
                    response = real_server.recv(1024)
                    client_socket.send(response)
                    #log
                    log_message(f'STAT - SUCCESSFUL', client_socket)
                elif data.upper().startswith('NOOP'):
                    real_server.sendall(b'NOOP\r\n')
                    response = real_server.recv(1024)
                    client_socket.send(response)
                    #log
                    log_message(f'NOOP - SUCCESSFUL', client_socket)
                elif data.upper().startswith('RSET'):
                    real_server.sendall(b'RSET\r\n')
                    response = real_server.recv(1024)
                    client_socket.send(response)
                    #log
                    log_message(f'RSET - SUCCESSFUL', client_socket)
                elif data.upper().startswith('TOP') and admin:
                    message_number = data.split()[1]
                    num_lines = data.split()[2]
                    real_server.sendall(f'TOP {message_number} {num_lines}\r\n'.encode('utf-8'))
                    response = real_server.recv(4096)
                    client_socket.send(response)
                    #log
                    log_message(f'TOP - SUCCESSFUL', client_socket)
                elif data.upper().startswith('TOP') and not admin:
                    client_socket.send(b'-ERR Only admin can view message headers\r\n')
                    #log
                    log_message(f'TOP - UNSUCCESSFUL', client_socket)
                elif data.upper().startswith('UIDL'):
                    if not admin:
                        #Get how many messages are in the new list
                        #Build response with the new_list
                        response = f'+OK\r\n';
                        index = 1;
                        for line in new_list_uidl:
                            #Starting from 1, list the message number as the index
                            #Remove the message number from the line
                            response += f'{index} {line.split()[1]}\r\n'
                            index += 1
                        #Add a period to the end of the response
                        response += '.\r\n'
                        client_socket.send(response.encode('utf-8'))
                        log_message(f'UIDL - SUCCESSFUL', client_socket)
                    else:
                        real_server.sendall(b'UIDL\r\n')
                        response = real_server.recv(4096)
                        client_socket.send(response)
                        #log
                        log_message(f'UIDL - SUCCESSFUL', client_socket)
                elif data.upper().startswith('CAPA'):
                    response = b'+OK\r\n'
                    response += b'CAPA\r\n'
                    response += b'TOP\r\n'
                    response += b'UIDL\r\n'
                    response += b'.\r\n'     
                    client_socket.send(response.encode('utf-8'))        
                else:
                    if client_socket:
                        client_socket.send(b'-ERR Invalid command\r\n')
                        #log which command was sent without the socket details
                        print(f'Invalid command: {data}')

            real_server.close()
    except BrokenPipeError:
        print('Connection closed by client')
    except ConnectionResetError:
        print('Connection reset by client')
    finally:
        client_socket.close()

def filter_confidential(data):
    subject = None
    lines = data.split('\n')
    for line in lines:
        if line.lower().startswith('subject:'):
            subject = line.strip()
            break
    return subject and 'confidential' in subject.lower()

def log_message(data, client_socket):
    client_ip = client_socket.getpeername()[0]
    datetime_object = datetime.datetime.now()
    print(f'{datetime_object} - {client_ip} - {data}')

def start_proxy():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((PROXY_HOST, PROXY_PORT))
    server_socket.listen(5)
    print(f'Proxy server listening on port {PROXY_PORT}')

    while True:
        client_socket, addr = server_socket.accept()
        print(f'Accepted connection from {addr}')
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    start_proxy()
