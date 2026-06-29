# Get the simple string as output

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Hello from local server"}).encode())

server_address = ('0.0.0.0', 4443)
httpd = HTTPServer(server_address, MyHandler)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="certificates/cert.pem", keyfile="certificates/key.pem")
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("Server running on https://0.0.0.0:4443")
httpd.serve_forever()


