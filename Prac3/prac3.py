#!/usr/bin/python3
# Written by Lloyd Creighton u04954336 and Yi-Rou (Monica) Hung u22561154

import socket

def process_request(request, numbers):
	path = request.split()[1]
	if path == '/':
		return numbers
	if path == '/next':
		next = numbers[1] + numbers[2]
		numbers[0] = numbers[1]
		numbers[1] = numbers[2]
		numbers[2] = next
		return numbers
	if path == '/prev':
		prev = numbers[1] - numbers[0]
		if(numbers[0] <= 0):
			return numbers
		numbers[2] = numbers[1]
		numbers[1] = numbers[0]
		numbers[0] = prev
		return numbers
	return None

def create_response(numbers):
	numberString = ', '.join(str(num) for num in numbers)
	prev_resp = '<a href = "prev" style="color: red;">Previous</a></p>' if numbers[0] > 0 else ''
	response = f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html lang= \"en\">
<head><title>The Fibonacci Sequence</title>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale = 1.0\">
<style>
body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; text-align:center; }}
h1 {{ background-color: #f2f2f2; padding: 10px; }}
p {{ margin-top: 10px; }}
a {{ color: blue; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>The Fibonacci Sequence</h1>
<p style='font-weight: bold;'>Current Fibonacci Numbers: {numberString}</p>
<p><a href="/next" style = "color: green;">Next</a></p>
{prev_resp}
</body>
</html>
"""
	return response

def run_server():
	host = '127.0.0.1'
	port = 5555
	numbers = [0, 1, 1]

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
		server_socket.bind((host, port))
		server_socket.listen(1)
		print(f"Server listening on {host}:{port}")
		
		while True:
			client_socket, addr = server_socket.accept()
			with client_socket:
				request = client_socket.recv(1024).decode('utf-8')
				print(f"Received request from {addr}:")
				print(request)

				if not request:
					response = """HTTP/1.1 400 Bad Request
"""
					client_socket.sendall(response.encode('utf-8'))
				else:
					type = request.split()[0]
					httpcheck = None
					if len(request.split()) >= 3:
						httpcheck = request.split()[2]
					if httpcheck is not None and httpcheck == "HTTP/1.1":

						if type == 'HEAD':
							response = """HTTP/1.1 200 OK
		Content-Type: text/html

		<!DOCTYPE html>
		<html lang= \"en\">
		<head><title>The Fibonacci Sequence</title>
		<meta charset=\"utf-8\">
		<meta name=\"viewport\" content=\"width=device-width, initial-scale = 1.0\">
"""
							client_socket.sendall(response.encode('utf-8'))
						elif type == "GET":
							result = process_request(request, numbers)
							if result is not None:
								numbers = result
								response = create_response(numbers)
								client_socket.sendall(response.encode('utf-8'))
							else:
								response = """HTTP/1.1 404 Not Found
"""
								client_socket.sendall(response.encode('utf-8'))
						else:
							response = """HTTP/1.1 400 Bad Request
"""
							client_socket.sendall(response.encode('utf-8'))
					else:
						response = """HTTP/1.1 400 Bad Request
"""
						client_socket.sendall(response.encode('utf-8'))

if __name__ == "__main__":
	run_server()
