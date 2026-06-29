import json
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/products":
            conn = sqlite3.connect("products.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, stock, imageUrl, desc, rating FROM products")
            rows = cursor.fetchall()
            conn.close()

            products = [
                {"id": r[0], "name": r[1], "price":r[2], "stock":r[3], "imageUrl":r[4], "desc":r[5], "rating":r[6]} for r in rows
            ]


            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps(products).encode())

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")


    def do_POST(self):

        if self.path == "/add-product":

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)

                name = data["name"]
                price = data["price"]
                stock = data["stock"]
                imageUrl = data["imageUrl"]
                desc = data["desc"]
                rating = data["rating"]

                conn = sqlite3.connect("products.db")
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO products (name, price, stock, imageUrl, desc, rating) VALUES (?,?,?,?,?,?)",(name, price, stock, imageUrl, desc, rating)
                )

                conn.commit()
                conn.close()

                response = {"status": "product inserted"}

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                self.wfile.write(json.dumps(response).encode())
            
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

if __name__ == "__main__":
    server_address = ('0.0.0.0', 4443)
    httpd = HTTPServer(server_address, MyHandler)

    print("Server running on http://<YOUR-PC-IP>:4443")
    print("GET /products to fetch products")
    print("POST /add-product to add products (JSON body: name, price, stock)")
    httpd.serve_forever()