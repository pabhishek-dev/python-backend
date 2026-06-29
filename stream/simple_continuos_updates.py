import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        if self.path == "/events":
            self.send_response(200)
            self.send_header("Content-type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            while True:
                data = json.dumps({"message": "Server update"})
                self.wfile.write(f"data: {data}\n\n".encode())
                self.wfile.flush()
                time.sleep(5)

server_address = ('0.0.0.0', 4443)
httpd = HTTPServer(server_address, MyHandler)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("Server running on https://0.0.0.0:4443")
httpd.serve_forever()