'''
How to test?

1. Run this script in one console. `python job_scheduler_executor.py`. Notice this will open port 8080
2. In another console, Send an HTTP request to the sever. `curl http://localhost:8080`
3. Observe the log output in the first console.
'''

import threading
import time
import random
from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"New job received\n")
        
        # Set the event to wake up the main loop
        self.server.new_job_event.set()

def main_loop(new_job_event):
    print("[main thread] Loaded all active jobs from DB. (Simulation)")
    print("[main thread] Store all active jobs to Min-heap according to next_time. (Simulation)")
    print("[main thread] entering sleep")
    while True:
        sleep_sec = random.randint(1, 10)
        print(f"[main thread] sleep for {sleep_sec} seconds")
        new_job_event.wait(timeout=sleep_sec)

        if new_job_event.is_set():
            print("[main thread] waked up by newly registered job")
            new_job_event.clear()  # Clear the event; Threading.Event is thread-safe in Python
        else:
            print("[main thread] waked up from due sleep time")

        print("[main thread] pop min heap; process due jobs; re-inserted active jobs to heap. (Simulation)")

def server_thread(new_job_event):
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.new_job_event = new_job_event
    print("[server thread] HTTP server is running on port 8080")
    httpd.serve_forever()


new_job_event = threading.Event()

# Create and start the main thread
main_thread = threading.Thread(target=main_loop, args=(new_job_event,))
main_thread.start()

# Create and start the server thread
server_thread = threading.Thread(target=server_thread, args=(new_job_event,))
server_thread.start()




main_thread.join()
