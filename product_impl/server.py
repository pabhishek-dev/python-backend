import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import db # import db module

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/products":
            products = db.fetch_products()
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

                # handle single or multiple products
                if isinstance(data, list):
                    db.insert_products(data)
                else:
                    db.insert_product(data)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "product(s) inserted"}).encode())

            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())


if __name__ == "__main__":
    server_address = ('0.0.0.0', 4443)
    httpd = HTTPServer(server_address, MyHandler)
    print("Server running on http://<YOUR-PC-IP>:4443")
    print("GET /products to fetch products")
    print("POST /add-product to add products")
    httpd.serve_forever()