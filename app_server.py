from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import threading
import queue
import concurrent.futures
import json
import argparse
import sys
import time


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.semaphore.acquire()
        try:
            # Read the incoming request data
            content_length = int(self.headers['Content-Length'])
            request_data = self.rfile.read(content_length)

            # Get the client's address
            client_address = self.client_address
            print(f"received incoming request from {client_address}")

            with self.server.lock:
                self.server.num_ongoing_requests += 1
                num_ongoing_requests = self.server.num_ongoing_requests

            response_data = self.heavy_lifting_job(
                request_data, client_address, num_ongoing_requests, self.server.options)
            response_json = json.dumps(response_data).encode('utf-8')

            print(f"response ready for {client_address}")

            # Send the result back to the client
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_json)))
            self.end_headers()
            self.wfile.write(response_json)
            self.wfile.flush()
        finally:
            with self.server.lock:
                self.server.num_ongoing_requests -= 1
            self.server.semaphore.release()

    def heavy_lifting_job(self, request_data, client_address, num_ongoing_requests, options):
        n = num_ongoing_requests
        load_factor = 9 * n / 19 + 10 / 19
        # Simulate variable processing time based on the number of ongoing requests
        cpu_time = options.cpu_time_ms * load_factor
        io_time = options.io_time_ms * load_factor

        # Simulate CPU-bound processing
        time.sleep(cpu_time / 1000.0)  # Convert ms to seconds
        # Simulate I/O-bound processing
        time.sleep(io_time / 1000.0)  # Convert ms to seconds

        response = {
            'message': 'Request processed successfully',
            'client': client_address,
            'request_data': request_data.decode('utf-8')
        }
        return response

        # Enable logging to avoid printing each request to the stdout
        def log_message(self, format, *args):
            return


def start_server(options):
    # Use ThreadingMixIn to handle requests in separate threads
    class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
        def __init__(self, server_address, RequestHandlerClass, options):
            # Call the parent class's initializer
            super().__init__(server_address, RequestHandlerClass)
            self.options = options
            self.semaphore = threading.Semaphore(options.num_thread)
            self.num_ongoing_requests = 0  # Initialize the counter for ongoing requests
            self.lock = threading.Lock()  # Initialize the lock for thread-safe counter access

    # Define the server and handler
    server_address = ('', options.port)

    httpd = ThreadingHTTPServer(
        server_address, RequestHandler, options=options)

    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print(f"Serving on port {server_address[1]}")

    try:
        while server_thread.is_alive():
            server_thread.join(timeout=1)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down server...")
        httpd.shutdown()
        httpd.server_close()
        print("Server shut down gracefully.")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Custom HTTP server with request queue and multiprocessing.')
    parser.add_argument('--port', type=int, default=7100,
                        help='Port number')
    parser.add_argument('--num_thread', type=int, default=3,
                        help='Number of concurrent thread that accepts incoming requests')
    parser.add_argument('--cpu_time_ms', type=int, default=100,
                        help='CPU processing time in milliseconds')
    parser.add_argument('--io_time_ms', type=int, default=300,
                        help='I/O processing time in milliseconds')

    args = parser.parse_args()
    start_server(args)
