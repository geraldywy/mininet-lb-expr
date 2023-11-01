import SimpleHTTPServer
import SocketServer


class OverrideHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    servers = ["http://10.0.0.7", "http://10.0.0.8", "http://10.0.0.9"]

    def do_GET(self):
        algo = self.headers.get("algo", "RR")
        self.send_response(301)

        if algo.lower() == "rr":
            addr = self.RR(self.server.c, self.servers)
        else:
            addr = self.servers[0]

        self.server.c += 1
        self.send_header("Location", addr)
        self.end_headers()

    @staticmethod
    def RR(c, servers):
        n = c % len(servers)
        return servers[n]


class HTTPServerWithCount(SocketServer.TCPServer):
    c = 0  # Initialize the request count


# Create a server to handle HTTP requests using the overridden handler
PORT = 80
httpd = HTTPServerWithCount(("", PORT), OverrideHandler)

httpd.serve_forever()
