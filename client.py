import argparse
import asyncio
import aiohttp
import time


async def fetch(session, url):
    # Measure the time before sending the requests
    start_time = time.time_ns() / 1e6
    async with session.post(url, json={}) as response:
        resp = await response.json()
        # Calculate the round-trip time
        end_time = time.time_ns() / 1e6
        round_trip_time = end_time - start_time
        result = f"[{round_trip_time:.2f}ms] {resp}"
        print(result)
        return result


async def make_requests(url, num_requests):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_requests):
            tasks.append(fetch(session, url))
        results = await asyncio.gather(*tasks)
        return results


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Simple HTTP client.')
    parser.add_argument('--server', type=str,
                        default='127.0.0.1', help='Server IP address')
    parser.add_argument('--port', type=int, default=7100, help='Server port')
    parser.add_argument('--concurrent', type=int, default=17,
                        help='Number of concurrent requests')

    # Parse arguments
    args = parser.parse_args()
    server_ip = args.server
    server_port = args.port
    num_requests = args.concurrent

    # Construct the URL
    url = f'http://{server_ip}:{server_port}'

    # Make the concurrent requests
    try:
        results = asyncio.run(make_requests(url, num_requests))

    except aiohttp.ClientError as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
