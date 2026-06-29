# Get the complete folder from the desktop

import http.server
import ssl

server_address = ('0.0.0.0', 4443)
httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)

httpd.socket = ssl.wrap_socket(
    httpd.socket,
    certfile="cert.pem",
    keyfile="key.pem",
    server_side=True
)

print("Server running on https://192.168.1.10:4443")
httpd.serve_forever()