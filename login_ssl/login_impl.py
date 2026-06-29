# Login implementation on ssl

from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json
import sqlite3

# Create DB
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()


class MyHandler(BaseHTTPRequestHandler):

    def do_POST(self):

        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length)
        data = json.loads(body)

        if self.path == "/register":

            try:
                cursor.execute(
                    "INSERT INTO users(username,password) VALUES (?,?)",
                    (data["username"], data["password"])
                )
                conn.commit()

                response = {"status": "registered"}

            except:
                response = {"status": "user_exists"}

        elif self.path == "/login":

            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (data["username"], data["password"])
            )

            user = cursor.fetchone()

            if user:
                response = {"status": "login_success"}
            else:
                response = {"status": "invalid_credentials"}

        else:
            response = {"status": "unknown_endpoint"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(json.dumps(response).encode())


server_address = ('0.0.0.0', 4443)
httpd = HTTPServer(server_address, MyHandler)

httpd.socket = ssl.wrap_socket(
    httpd.socket,
    certfile="certificates/cert.pem",
    keyfile="certificates/key.pem",
    server_side=True
)

print("Server running on <Your-IP>:4443")
httpd.serve_forever()