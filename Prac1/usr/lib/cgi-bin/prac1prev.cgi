#!/usr/bin/python3
# Written by Lloyd Creighton u04954336 and Yi-Rou (Monica) Hung u22561154

with open('prac1.txt', 'r') as file:
    numbers = [int(num) for num in file.read().splitlines()]

prev = numbers[1] - numbers[0]

if prev >= 1:
    with open('prac1.txt', 'w') as file:
        file.write('\n'.join([str(prev), str(numbers[0]), str(numbers[1])]))

with open('prac1.txt', 'r') as file:
    numbers = [int(num) for num in file.read().splitlines()]

print("Content-type: text/html\n")
print("<!DOCTYPE html>")
print("<html lang =\"en\">")
print("<head><title>The Fibonacci Sequence</title>")
print("<meta charset=\"utf-8\">")
print("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
print('<style>')
print('body { font-family: Arial, sans-serif; margin: 0; padding: 0; text-align:center; }')
print('h1 { background-color: #f2f2f2; padding: 10px; }')
print('p { margin-top: 10px; }')
print('a { color: blue; text-decoration: none; }')
print('a:hover { text-decoration: underline; }')
print('</style>')
print("</head>")
print("<body>")
print("<h1>The Fibonacci Sequence</h1>")
print(f"<p style='font-weight: bold;'>Current Fibonacci Numbers: {', '.join(map(str, numbers))}</p>")
print('<p><a href="/cgi-bin/prac1next.cgi" style="color: green;">Next</a></p>')

if numbers[1] > 1:
    print('<p><a href="/cgi-bin/prac1prev.cgi" style="color: red;">Previous</a></p>')
print("</body>")
print("</html>")
