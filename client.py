import argparse
import asyncio
import aiohttp
import time


async def fetch(session, url):
    # Measure the time before sending the requests
    start_time = time.time_ns() / 1e6
    try:
        async with session.post(url, json={}) as response:
            resp = await response.json()
            # Calculate the round-trip time
            end_time = time.time_ns() / 1e6
            round_trip_time = end_time - start_time
            result = f"[{round_trip_time:.2f}ms] {resp}"
            print(result)
            return result
    except Exception as err:
        round_trip_time = float('inf')
        error_message = str(err)
        print("Request failed:", error_message)
        return error_message


async def make_requests(url, options):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=options.timeout)) as session:
        tasks = []
        for _ in range(options.num_requests):
            tasks.append(fetch(session, url))
        results = await asyncio.gather(*tasks)
        return results


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Simple HTTP client.')
    parser.add_argument('--server', type=str,
                        default='127.0.0.1', help='Server IP address')
    parser.add_argument('--port', type=int, default=7100, help='Server port')
    parser.add_argument('--num_requests', type=int, default=17,
                        help='Number of concurrent requests')
    parser.add_argument('--timeout', type=int, default=5,
                        help='timeout in seconds')

    # Parse arguments
    args = parser.parse_args()
    server_ip = args.server
    server_port = args.port
    options = args

    # Construct the URL
    url = f'http://{server_ip}:{server_port}'

    # Make the concurrent requests
    try:
        results = asyncio.run(make_requests(url, options))

    except aiohttp.ClientError as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
