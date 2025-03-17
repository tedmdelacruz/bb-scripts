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

# Directory to save webpages
DOWNLOADS_DIR = 'fetched-webpages'

def generate_random_string(length=16):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters.lower(), k=length))

# Function to download a single JS file
def download_js_file(url, webpage_url, verbose):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.join(DOWNLOADS_DIR, generate_random_string() + ".js")
            with open(filename, 'wb') as file:
                file.write(f"// Webpage URL: {webpage_url}\n".encode())
                file.write(f"// Source: {url}\n".encode())
                file.write(response.content)
            if verbose:
                secho(f"[OK] {url}", fg='green')
        else:
            if verbose:
                secho(f"[FAILED] {url} - HTTP status: {response.status_code}", fg='red')
    except Exception as e:
        if verbose:
            secho(f"[FAILED] {url}", fg='red')

# Function to download a single webpage
def download_webpage(url, verbose):
    try:
        response = requests.get(url)
        filename = os.path.join(DOWNLOADS_DIR, generate_random_string() + ".html")
        with open(filename, 'wb') as file:
            file.write(f"<!-- Webpage URL: {url}-->\n".encode())
            file.write(response.content)
        if verbose:
            secho(f"[OK] {url}", fg='green')
    except Exception as e:
        if verbose:
            secho(f"[FAILED] {url}", fg='red')

def fetch_website(url, verbose):
    """Fetches the HTML content of the website and all of its JavaScript resources"""
    try:
        response = requests.get(url)
        if verbose:
            secho(f"[INFO] Downloading webpage at {url}...", fg="bright_black")
        download_webpage(url, verbose)
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
            if verbose:
                secho(f"[INFO] No JS files in {url}", fg="bright_black")
            return
        if verbose:
            secho(f"[INFO] Downloading {len(js_files)} JS files at {url}...", fg="bright_black")
        for js_file in js_files:
            if not any(lib in js_file for lib in COMMON_LIBRARIES):
                download_js_file(urljoin(url, js_file), url, verbose)
    except Exception:
        pass

@command()
@option('-t', '--threads', default=1, help='Number of threads to use')
@option('-v', '--verbose', is_flag=True, help='Print verbose logs')
def main(threads, verbose):
    websites = [line.strip() for line in sys.stdin]
    if len(websites) == 0:
        secho("No URLs received from STDIN", fg="red")
        return

    if verbose:
        secho("Running script...", fg="blue")

    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    queue = Queue()
    if verbose:
        secho(f"Received {len(websites)} websites", fg="blue")
    for website in websites:
        queue.put(website)

    def worker():
        while not queue.empty():
            url = queue.get()
            fetch_website(url, verbose)
            queue.task_done()

    threads = [threading.Thread(target=worker) for _ in range(threads)]
    for thread in threads:
        thread.start()

    queue.join()
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()
