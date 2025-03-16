import os
import requests
import threading
import sys
import uuid
import time
import random
import string
from queue import Queue
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from click import command, option, secho, style

# List of common libraries to ignore
COMMON_LIBRARIES = [
    'jquery', 'bootstrap', 'angular', 'react', 'vue', 'lodash', 'moment', 'underscore'
]

# Directory to save JS files
JS_DIR = 'js-files'

def generate_random_string(length=16):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# Function to download a single JS file
def download_js_file(url, verbose):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.join(JS_DIR, generate_random_string() + ".js")
            with open(filename, 'wb') as file:
                file.write(f"// Source: {url}\n".encode())
                file.write(response.content)
            if verbose:
                secho(f"[OK] {url}", fg='green')
        else:
            if verbose:
                secho(f"[FAILED] {url} - HTTP status: {response.status_code}", fg='red')
    except Exception as e:
        if verbose:
            secho(f"[FAILED] {url} - {e}", fg='red')

# Function to extract JS files from a webpage
def extract_js_files(url, verbose):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content, 'html.parser')
        js_files = set()
        for script in soup.find_all('script'):
            src = script.get('src')
            if src:
                js_files.add(src)
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href and href.endswith('.js'):
                js_files.add(href)
        if len(js_files) == 0:
            return
        if verbose:
            secho(f"Found {len(js_files)} JS files at {url}")
        for js_file in js_files:
            if not any(lib in js_file for lib in COMMON_LIBRARIES):
                download_js_file(urljoin(url, js_file), verbose)
    except Exception as e:
        pass

# Function to process a single website
def process_website(url, verbose):
    extract_js_files(url, verbose)
    # Additional logic to handle async loaded JS files can be added here

# Main function to handle the CLI
@command()
@option('-t', '--threads', default=1, help='Number of threads to use')
@option('-v', '--verbose', is_flag=True, help='Print verbose logs')
def main(threads, verbose):
    if not os.path.exists(JS_DIR):
        os.makedirs(JS_DIR)

    websites = [line.strip() for line in sys.stdin]
    queue = Queue()

    for website in websites:
        queue.put(website)

    def worker():
        while not queue.empty():
            url = queue.get()
            process_website(url, verbose)
            queue.task_done()

    threads = [threading.Thread(target=worker) for _ in range(threads)]
    for thread in threads:
        thread.start()

    queue.join()
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()