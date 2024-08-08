#!/usr/bin/python3

import socket
import random
import poplib
import threading


score = 0
totalQuestions = 1

def send_mail(score, total):
    smtp_server = '127.0.0.1'
    smtp_port = 25
    sender_email = 'admin@localhost.com'
    recipient_email = 'lloyd@localhost.com'
    message = """Subject: Thank you for taking our Quiz!\n\n Your score was: {}/{}""".format(score, total)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mail_socket:
        mail_socket.connect((smtp_server, smtp_port))
        mail_socket.sendall(b"HELO localhost\r\n")
        mail_socket.recv(1024)
        mail_socket.sendall(f"MAIL FROM: {sender_email}\r\n".encode())
        mail_socket.recv(1024)
        mail_socket.sendall(f"RCPT TO: {recipient_email}\r\n".encode())
        mail_socket.recv(1024)
        mail_socket.sendall(b"DATA\r\n")
        mail_socket.recv(1024)
        mail_socket.sendall(message.encode())
        mail_socket.sendall(b"\r\n.\r\n")
        mail_socket.recv(1024)
        mail_socket.sendall(b"QUIT\r\n")

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

def send_html_response(conn, content):
    html_response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Quiz</title>
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: flex-start;
                    height: 100vh;
                    margin: 0;
                }}
                .content {{
                    margin-top: 20px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="content">
                {content}
            </div>
        </body>
        </html>"""
    conn.sendall(html_response.encode())

def handle_client(conn, questions):
    global score
    global totalQuestions
    data = conn.recv(1024)
    if not data:
        # print("No data received")
        err_response = b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nConnection closed due to no data received"
        conn.sendall(err_response)
        conn.close()
    try:
        url = data.decode().split('\n')[0].split()[1]
    except IndexError:
        print("Invalid request format")
        conn.sendall(b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nBad Request")
        conn.close()

    if 'answer' in url:
        query_string = url.split('?')[-1]
        query_params = dict(param.split("=") for param in query_string.split("&"))
        user_answer = query_params.get('answer', '').lower()
        correct_answer = query_params.get('correct_answer', '').lower()

        response = ''
        if user_answer == correct_answer:
            response = "Correct!"
            score += 1
        else:
            response = f"Incorrect. The correct answer was: {correct_answer.replace('+', ' ')}"

        content = f"""
            <h1>{response}</h1>
            <form method="GET" action="/next_question">
                <label for="choice">Would you like another question?</label>
                <input type="text" id="choice" name="choice" placeholder="yes/no">
                <input type="submit" value="Submit">
            </form>
        """
        send_html_response(conn, content)
    elif 'choice' in url:
        query_string = url.split('?')[-1]
        query_params = dict(param.split("=") for param in query_string.split("&"))
        user_choice = query_params.get('choice', '').lower()
        if user_choice not in {'yes', 'no'}:
            send_mail(score, totalQuestions)
            content = """
                <h1>Goodbye</h1>
                <p>An email has been sent to you with your score!</p>
            """
            score = 0
            totalQuestions = 1
            send_html_response(conn, content)
            conn.close()


        if user_choice == 'no':
            send_mail(score, totalQuestions)
            content = """
                <h1>Goodbye</h1>
                <p>An email has been sent to you with your score!</p>
            """
            score = 0
            totalQuestions = 1
            send_html_response(conn, content)
            conn.close()


        elif user_choice == 'yes':
            question = random.choice(questions)
            content = f"""
                <h1>{question['question']}</h1>
                <form method="GET" action="/submit">
                    {"".join(f'<input type="radio" name="answer" value="{answer}"> {answer}<br>' for answer in question['answers'])}
                    <input type="hidden" name="correct_answer" value="{question['correct']}">
                    <input type="submit" value="Submit">
                </form>
            """
            totalQuestions += 1
            send_html_response(conn, content)
    else:
        question = random.choice(questions)
        content = f"""
            <h1>{question['question']}</h1>
            <form method="GET" action="/submit">
                {"".join(f'<input type="radio" name="answer" value="{answer}"> {answer}<br>' for answer in question['answers'])}
                <input type="hidden" name="correct_answer" value="{question['correct']}">
                <input type="submit" value="Submit">
            </form>
        """
        send_html_response(conn, content)
        conn.close()

def main():
    questions = load_questions('questions.txt')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 5555))
    server_socket.listen(5)

    print("Server is waiting for a connection...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn, questions))
        client_thread.start()

if __name__ == '__main__':
    main()
