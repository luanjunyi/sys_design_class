from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import threading
import queue
import concurrent.futures
import json
import argparse
import sys
import time


def heavy_lifting_job(request_data, client_address, options):
    # Simulate CPU-bound processing
    time.sleep(options.cpu_time_ms / 1000.0)  # Convert ms to seconds
    # Simulate I/O-bound processing
    time.sleep(options.io_time_ms / 1000.0)  # Convert ms to seconds

    response = {
        'message': 'Request processed successfully',
        'client': client_address,
        'request_data': request_data.decode('utf-8')
    }
    return response


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the incoming request data
        content_length = int(self.headers['Content-Length'])
        request_data = self.rfile.read(content_length)

        # Get the client's address
        client_address = self.client_address
        print(f"received incoming request from {client_address}, will enqueue")
        # Process the request with the worker pool
        future = self.server.worker_pool.submit(
            heavy_lifting_job, request_data, client_address, self.server.options)
        response_data = future.result()
        response_json = json.dumps(response_data).encode('utf-8')

        print(f"response ready for {client_address}")

        # Send the result back to the client
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_json)))
        self.end_headers()
        self.wfile.write(response_json)
        self.wfile.flush()

    # Enable logging to avoid printing each request to the stdout
    def log_message(self, format, *args):
        return


def start_server(options):
    # Define the server and handler
    server_address = ('', options.port)

    # Use ThreadingMixIn to handle requests in separate threads
    class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
        def __init__(self, server_address, RequestHandlerClass, worker_pool, options):
            # Call the parent class's initializer
            super().__init__(server_address, RequestHandlerClass)
            self.worker_pool = worker_pool
            self.options = options

    # Create a pool of workers
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as worker_pool:
        httpd = ThreadingHTTPServer(
            server_address, RequestHandler, worker_pool=worker_pool, options=args)

        # Start the server in a separate thread
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
            worker_pool.shutdown(wait=True)
            print("Server shut down gracefully.")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Custom HTTP server with request queue and multiprocessing.')
    parser.add_argument('--port', type=int, default=7100,
                        help='Port number (default: 7100)')
    parser.add_argument('--workers', type=int, default=3,
                        help='Number of concurrent processes in the pool (default: 4)')
    parser.add_argument('--cpu_time_ms', type=int, default=1000,
                        help='CPU processing time in milliseconds (default: 1000ms)')
    parser.add_argument('--io_time_ms', type=int, default=3000,
                        help='I/O processing time in milliseconds (default: 3000ms)')

    args = parser.parse_args()
    start_server(args)
