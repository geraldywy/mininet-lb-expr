import SimpleHTTPServer
import SocketServer
import os
import random
import time

class OverrideHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.server.update_new_active_conn()
        server_id = os.environ.get("server_id")
        # to simulate increasing latency with load, we add .5s for each active request in the past 10s
        base_resp_timer = len(self.server.conn_timestamps) * 0.5

        is_faulty = os.environ.get("is_faulty", "0")
        if is_faulty > random.randint(0, 1) / 100:
            # Generate a random delay multiple between 2x to 5x for faulty servers
            random_delay = random.uniform(2, 5)
            base_resp_timer *= random_delay

        time.sleep(base_resp_timer)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("server_id", server_id)
        self.end_headers()
        self.wfile.write("Hello from server " + server_id + " ! "+"number of open conns: " + str(len(self.server.conn_timestamps)))


class HTTPServerWithActiveConnCounter(SocketServer.TCPServer):
    conn_timestamps = []

    def update_new_active_conn(self):
        now = time.time()
        self.conn_timestamps.append(now) # append req timestamp
        # Remove timestamps older than 20 seconds
        self.conn_timestamps = [ts for ts in self.conn_timestamps if now - ts <= 20]

httpd = HTTPServerWithActiveConnCounter(("", 80), OverrideHandler)

print "serving at port 80"
httpd.serve_forever()
