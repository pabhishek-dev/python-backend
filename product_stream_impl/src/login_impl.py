# Login implementation on ssl

from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json
import sqlite3
import jwt
import bcrypt
import datetime

from config import DB_PATH, CERT_PATH, KEY_PATH, JWT_SECRET, LOGIN_PORT


conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

class MyHandler(BaseHTTPRequestHandler):

    def do_POST(self):

        length = int(self.headers.get('Content-Length',0))
        if length == 0:
            self.send_error(400, "Bad Request: No data provided")
            return
        
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
            username = data["username"]
            password = data["password"]
        except (json.JSONDecodeError, KeyError):
            self.send_error(400, "Bad Request: Invalid JSON or missing fields")
            return

        data = json.loads(body)

        if self.path == "/register":

            try:

                salt = bcrypt.gensalt()
                hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)

                cursor.execute(
                    "INSERT INTO users(username,password) VALUES (?,?)",
                    (data["username"], hashed_pw.decode('utf-8'))
                )
                conn.commit()

                response = {"status": "registered"}

            except sqlite3.IntegrityError:
                response = {"status": "user_exists"}

        elif self.path == "/login":

            cursor.execute(
                "SELECT password FROM users WHERE username=?",(username,)
                )
            
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):

                # Generate a JWT token valid for 1 hour

                expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
                jwt_payload = {
                    "username": username,
                    "exp": expiration_time
                }

                token = jwt.encode(jwt_payload, JWT_SECRET, algorithm="HS256")

                response = {
                    "status": "login_success",
                    "token": token
                    }
            else:
                response = {"status": "invalid_credentials"}

        else:
            response = {"status": "unknown_endpoint"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(json.dumps(response).encode())


server_address = ('0.0.0.0', LOGIN_PORT)
httpd = HTTPServer(server_address, MyHandler)

context = ssl.SSLContext( ssl.PROTOCOL_TLS_SERVER)
    
context.minimum_version = ssl.TLSVersion.TLSv1_2

context.load_cert_chain(
    certfile = CERT_PATH,
    keyfile = KEY_PATH,
)

httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("Server running on https://<YOUR-PC-IP>:4443")
httpd.serve_forever()