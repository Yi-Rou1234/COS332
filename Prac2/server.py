# u22561154 (Yi-Rou Hung), u04954336 (Lloyd Creighton)
import socket
import random
import threading

ESC = chr(27)

def clear_screen(conn):
    conn.sendall(f'{ESC}[2J'.encode())

def move_cursor(conn, x, y):
    conn.sendall(f'{ESC}[{y};{x}H'.encode())

def load_questions(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    questions = []
    question = None

    for line in lines:
        if line.startswith('?'):
            if question:
                questions.append(question)
            question = {'question': line[1:].strip(), 'answers': [], 'correct': None}
        elif line.startswith('-'):
            question['answers'].append(line[1:].strip())
        elif line.startswith('+'):
            question['answers'].append(line[1:].strip())
            question['correct'] = line[1:].strip()

    if question:
        questions.append(question)

    return questions

def handle_client(conn, questions):
    while True:
        clear_screen(conn)
        move_cursor(conn, 20, 5)
        question = random.choice(questions)
        conn.sendall((question['question'] + '\n').encode())
        for i, answer in enumerate(question['answers']):
            conn.sendall((f'{chr(65+i)}) {answer}\n').encode())

        data = conn.recv(1024)
        answer = data.decode().strip()
        if answer.lower() == question['correct'].lower():
            conn.sendall(b'Correct!\n')
        else:
            conn.sendall((f'Incorrect. The correct answer was: {question["correct"]}\n').encode())

        conn.sendall(b'Would you like another question? (yes/no)\n')
        data = conn.recv(1024)
        if data.decode().strip().lower() != 'yes':
            conn.close()
            break

def main():
    questions = load_questions('questions.txt')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5555))
    server_socket.listen(1)

    print("Server is waiting for a connection...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn, questions))
        client_thread.start()

if __name__ == '__main__':
    main()
