# import socket
# import random
# import threading
# from urllib.parse import urlparse, parse_qs

# def load_questions(filename):
#     with open(filename, 'r') as f:
#         lines = f.readlines()

#     questions = []
#     question = None

#     for line in lines:
#         if line.startswith('?'):
#             if question:
#                 questions.append(question)
#             question = {'question': line[1:].strip(), 'answers': [], 'correct': None}
#         elif line.startswith('-'):
#             question['answers'].append(line[1:].strip())
#         elif line.startswith('+'):
#             question['answers'].append(line[1:].strip())
#             question['correct'] = line[1:].strip()

#     if question:
#         questions.append(question)

#     return questions

# def handle_client(conn, questions):
#     while questions:
#         data = conn.recv(1024)
#         if not data:
#             print("No data received")
#             err_response = b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nConnection closed due to no data received"
#             conn.sendall(err_response)
#             conn.close()
#             break
#         try:
#             url = data.decode().split('\n')[0].split()[1]
#         except IndexError:
#             print("Invalid request format")
#             conn.sendall(b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nBad Request")
#             conn.close()
#             break

#         parsed_url = urlparse(url)
#         query_params = parse_qs(parsed_url.query)

import socket
import random
import threading

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

# def parse_url(url):
#     scheme, netloc, path, params, query, fragment = url.split('/', 5)
#     return scheme, netloc, path, params, query, fragment

def parse_url(url):
    parts = url.split('/')
    scheme = parts[0]
    netloc = parts[2] if len(parts) > 2 else ''
    path = parts[3] if len(parts) > 3 else ''
    params = parts[4] if len(parts) > 4 else ''
    query = parts[5] if len(parts) > 5 else ''
    fragment = parts[6] if len(parts) > 6 else ''
    return scheme, netloc, path, params, query, fragment

def parse_qs(query):
    params = query.split('&')
    query_params = {}
    for param in params:
        parts = param.split('=')
        if len(parts) == 2:
            key, value = parts
            query_params[key] = [value]
        else:
            query_params[parts[0]] = ['']
    return query_params


def handle_client(conn, questions):
    while questions:
        data = conn.recv(1024)
        if not data:
            print("No data received")
            err_response = b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nConnection closed due to no data received"
            conn.sendall(err_response)
            conn.close()
            break
        try:
            url = data.decode().split('\n')[0].split()[1]
        except IndexError:
            print("Invalid request format")
            conn.sendall(b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nBad Request")
            conn.close()
            break

        parsed_url = parse_url(url)
        query_params = parse_qs(parsed_url[4])

        # Rest of the code remains the same...
        

        if 'answer' in query_params:
            user_answer = query_params.get('answer', [''])[0]
            correct_answer = query_params.get('correct_answer', [''])[0]

            response = ''
            if user_answer.lower() == correct_answer.lower():
                response = "Correct!"
            else:
                response = f"Incorrect. The correct answer was: {correct_answer}"

            html_response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Quiz Response</title>
                </head>
                <body>
                    <h1>{response}</h1>
                    <form method="GET" action="/next_question">
                    <label for="choice">Would you like another question?</label>
                    <input type="text" id="choice" name="choice" placeholder="yes/no">
                    <input type="submit" value="Submit">
                    </form>
                </body>
                </html>"""

            conn.sendall(html_response.encode())

        elif 'choice' in query_params:
            user_choice = query_params.get('choice', [''])[0].lower()
            if user_choice not in {'yes', 'no'}:
                error_response = b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nInvalid choice, need to enter 'yes' or 'no'"
                conn.sendall(error_response)
                conn.close()
                break

            if user_choice == 'no':
                farewell_response = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Goodbye</title>
                    </head>
                    <body>
                        <h1>Goodbye</h1>
                        <p>Thank you for your time!</p>
                    </body>
                    </html>"""
                
                conn.sendall(farewell_response.encode())
                conn.close()
                break

            elif user_choice == 'yes':
                question = random.choice(questions)
                html_response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Quiz</title>
                    </head>
                    <body>
                        <h1>{question['question']}</h1>
                        <form method="GET" action="/submit">
                        {"".join(f'<input type="radio" name="answer" value="{answer}"> {answer}<br>' for answer in question['answers'])}
                        <input type="hidden" name="correct_answer" value="{question['correct']}">
                        <input type="submit" value="Submit">
                        </form>
                    </body>
                    </html>"""

                conn.sendall(html_response.encode())

        else:
            question = random.choice(questions)
            html_response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Quiz</title>
                </head>
                <body>
                    <h1>{question['question']}</h1>
                    <form method="GET" action="/submit">
                    {"".join(f'<input type="radio" name="answer" value="{answer}"> {answer}<br>' for answer in question['answers'])}
                    <input type="hidden" name="correct_answer" value="{question['correct']}">
                    <input type="submit" value="Submit">
                    </form>
                </body>
                </html>"""

            conn.sendall(html_response.encode())
            conn.close()
            break

def main():
    questions = load_questions('questions.txt')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
