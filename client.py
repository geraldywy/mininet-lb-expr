import os
import time
import urllib2
from datetime import datetime
import random

log_dir = "/home/mininet/log/"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


def send_request(algo):
    url = "http://10.0.0.6"  # Load balancer IP
    client_id = os.environ.get("client_id", "N/A")
    file_name = "{}{}_{}_monitor_{}.log".format(
        log_dir, client_id, algo, datetime.now().strftime("%Y%m%d_%H%M%S")
    )

    timer = os.environ.get("timer", "60")
    # Random interval between 0.1s to 5s for 1 minute
    end_time = time.time() + int(timer)
    while time.time() < end_time:
        try:
            start = time.time()
            req = urllib2.Request(url)
            req.add_header("algo", algo)
            response = urllib2.urlopen(req)
            server_id = response.headers.getheader("server_id", "N/A")
            time_taken = time.time() - start

            with open(file_name, "a") as log_file:
                log_file.write(
                    "Time: {:.2f}s - Server ID: {}\n".format(time_taken, server_id)
                )

        except urllib2.URLError as e:
            print("Request Exception:", e)

        interval = random.uniform(0.1, 1)  # Random interval
        time.sleep(interval)


# Run the request function
send_request(os.environ.get("algo", "RR"))
