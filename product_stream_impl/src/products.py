import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import db as db  # your database module
import ssl

from config import CERT_PATH, KEY_PATH, PRODUCTS_PORT

clients = []  # connected SSE clients


class MyHandler(BaseHTTPRequestHandler):

    # Handle CORS preflight
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_GET(self):
        # Normal product fetch
        if self.path == "/products":
            products = db.fetch_products()
            self.send_response(200)
            self.send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(products).encode())

        # SSE stream
        elif self.path == "/stream":
            self.send_response(200)
            self.send_cors_headers()
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            clients.append(self.wfile)
            print("Client connected for SSE")
            # Send existing products immediately
            existing_products = db.fetch_products()
            for product in existing_products:
                message = f"data: {json.dumps({'action': 'fetch', 'product': product})}\n\n"
                try:
                    self.wfile.write(message.encode())
                    self.wfile.flush()
                except:
                    clients.remove(self.wfile)
                    return
            # Keep connection alive — block until client disconnects
            import time
            try:
                while True:
                    time.sleep(1)
            except:
                if self.wfile in clients:
                    clients.remove(self.wfile)

        else:
            self.send_response(404)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/add-product":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data)

                if isinstance(data, list):
                    new_products = db.insert_products(data)
                else:
                    new_products = db.insert_product(data)
                    new_products = [new_products]

                # send update to all SSE clients
                for product in new_products:
                    message = f"data: {json.dumps({'action': 'insert', 'product': product})}\n\n"
                    dead_clients = []
                    for client in clients:
                        try:
                            client.write(message.encode())
                            client.flush()
                        except:
                            dead_clients.append(client)
                    for dc in dead_clients:
                        clients.remove(dc)

                self.send_response(200)
                self.send_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({'action': 'insert', "status": "product inserted"}).encode())

            except Exception as e:
                self.send_response(400)
                self.send_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_PUT(self):
        if self.path.startswith("/update-product"):
            product_id = int(self.path.split("/")[-1])

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data)

                db.update_product(product_id, data)

                updated_product = db.fetch_product(product_id)

                message = f"data: {json.dumps({'action': 'update', 'product': updated_product})}\n\n"

                dead_clients = []

                for client in clients:
                    try:
                        client.write(message.encode())
                        client.flush()
                    except:
                        dead_clients.append(client)
                
                for dc in dead_clients:
                    clients.remove(dc)
                
                self.send_response(200)
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "product updated"}).encode())

            except Exception as e:
                self.send_response(400)
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_DELETE(self):
        if self.path.startswith("/delete-product"):
            product_id = int(self.path.split("/")[-1])

            db.delete_product(product_id)

            message = f"data: {json.dumps({'action': 'delete', 'product': {'id':product_id}})}\n\n"

            dead_clients = []

            for client in clients:
                try:
                    client.write(message.encode())
                    client.flush()
                except:
                    dead_clients.append(client)
            
            for dc in dead_clients:
                clients.remove(dc)
            
            self.send_response(200)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "product delete"}).encode())

        elif self.path == "/delete-all-products":

            db.delete_all_products()

            message = f"data: {json.dumps({'action': 'delete_all'})}\n\n"

            dead_clients = []
            for client in clients:
                try:
                    client.write(message.encode())
                    client.flush()
                except:
                    dead_clients.append(client)

            for dc in dead_clients:
                clients.remove(dc)

            self.send_response(200)    
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status:": "all products deleted"}).encode())
        
        else:
            self.send_response(404)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b"Not Found")

if __name__ == "__main__":
    server_address = ('0.0.0.0', PRODUCTS_PORT)
    httpd = ThreadingHTTPServer(server_address, MyHandler)
    context = ssl.SSLContext( ssl.PROTOCOL_TLS_SERVER)
    
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    context.load_cert_chain(
        certfile = CERT_PATH,
        keyfile = KEY_PATH,
    )

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)


    print("HTTPS Server running on https://<YOUR-PC-IP>:4443")
    httpd.serve_forever()    