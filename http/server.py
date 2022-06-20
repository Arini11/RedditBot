import http.server
import socketserver


def iniciarServer():
    PORT = 8000

    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

iniciarServer()