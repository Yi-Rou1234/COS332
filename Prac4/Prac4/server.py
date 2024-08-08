import socket
import random
import threading

from urllib.parse import urlparse, parse_qs
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
    while questions:
        data = conn.recv(1024)
        if not data:
            # print("No data received")
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

        if 'answer' in url:
            query_params = dict(param.split("=") for param in urlparse(url).query.split("&"))
            user_answer = query_params.get('answer', '').lower()
            correct_answer = query_params.get('correct_answer', '').lower()

            response = ''
            if user_answer == correct_answer:
                response = "Correct!"
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
            query_params = dict(param.split("=") for param in urlparse(url).query.split("&"))
            user_choice = query_params.get('choice', '').lower()
            if user_choice not in {'yes', 'no'}:
                error_response = b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nInvalid choice, need to enter 'yes' or 'no'"
                conn.sendall(error_response)
                conn.close()
                break

            if user_choice == 'no':
                content = """
                    <h1>Goodbye</h1>
                    <p>Thank you for your time!</p>
                """
                send_html_response(conn, content)
                conn.close()
                break

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
