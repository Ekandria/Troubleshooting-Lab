from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import json


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Ask the API for the users
            response = urllib.request.urlopen(
                "http://localhost:5000/users"
            )

            data = json.loads(response.read())

            # Build a simple HTML page
            user_list = ""

            for user in data:
                user_list += (
                    f"<li>{user['name']} - {user['email']}</li>"
                )

            html = f"""
            <html>
            <head>
                <title>Troubleshooting Lab</title>
            </head>

            <body>
                <h1>Troubleshooting Lab</h1>

                <h2>Users</h2>

                <ul>
                    {user_list}
                </ul>
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.wfile.write(html.encode())

        except Exception as error:
            self.send_response(500)
            self.end_headers()

            self.wfile.write(
                f"Frontend error: {error}".encode()
            )


server = HTTPServer(("localhost", 8000), Handler)

print("Frontend running on http://localhost:8000")

server.serve_forever()



























