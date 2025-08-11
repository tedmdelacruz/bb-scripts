#!/usr/bin/env python3

"""
Keyword Hunter - Selenium-based Security Analysis Tool

This script analyzes web pages and JavaScript files for sensitive information using configurable
regex patterns. It handles dynamic content with Selenium, filters common JS libraries, and sends
Discord notifications for security findings. Designed for automated security assessment workflows.

Features:
- Dynamic content analysis with Selenium WebDriver
- Configurable regex patterns for different security categories
- JavaScript file discovery and analysis
- Discord notifications via discord-notify library
- Library filtering to reduce false positives
- Integration with reconnaissance pipelines

Usage:
    python3 keyword_hunter.py -u https://example.com -c config.yaml
    echo "https://example.com" | python3 keyword_hunter.py
"""

import sys
import re
import yaml
import argparse
import requests
import os
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from discord_notify import Notifier

# Common libraries to ignore (similar to js_downloader.py)
COMMON_LIBRARIES = [
    'jquery', 'bootstrap', 'angular', 'react', 'vue', 'lodash', 'moment', 
    'underscore', 'backbone', 'ember', 'knockout', 'mootools', 'prototype',
    'dojo', 'extjs', 'yui', 'zepto', 'axios', 'googleapis', 'cloudflare',
    'fontawesome', 'google-analytics', 'gtag', 'facebook', 'twitter', 'crazyegg',
    'gtm', 'polyfill', 'vendor'
]

class KeywordHunter:
    def __init__(self, config_file='config.yaml'):
        self.config = self.load_config(config_file)
        self.driver = None
        self.findings = []

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Config file {config_file} not found. Please create it using the sample config.")
            sys.exit(1)

    def setup_webdriver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(30)

    def is_common_library(self, url):
        """Check if URL contains common library patterns"""
        url_lower = url.lower()
        return any(lib in url_lower for lib in COMMON_LIBRARIES)

    def extract_js_urls(self, soup, base_url):
        """Extract JavaScript URLs from HTML"""
        js_urls = set()
        
        # Find script tags with src attributes
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and not self.is_common_library(src):
                full_url = urljoin(base_url, src)
                js_urls.add(full_url)
                
        return js_urls

    def get_js_content(self, js_url):
        """Fetch JavaScript content"""
        try:
            response = requests.get(js_url, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"Error fetching JS from {js_url}: {e}")
        return ""

    def search_keywords(self, content, content_type, source_url):
        """Search for keywords in content using regex patterns"""
        matches = []
        
        for keyword_group in self.config.get('keywords', []):
            group_name = keyword_group.get('name', 'Unknown')
            patterns = keyword_group.get('patterns', [])
            
            for pattern in patterns:
                try:
                    regex_matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in regex_matches:
                        matches.append({
                            'group': group_name,
                            'pattern': pattern,
                            'match': match.group(0),
                            'content_type': content_type,
                            'source_url': source_url,
                            'line_context': self.get_line_context(content, match.start())
                        })
                except re.error as e:
                    print(f"Invalid regex pattern '{pattern}': {e}")
                    
        return matches

    def get_line_context(self, content, position):
        """Get line context around a match position"""
        lines = content[:position].split('\n')
        line_num = len(lines)
        current_line = content.split('\n')[line_num - 1] if line_num <= len(content.split('\n')) else ""
        return f"Line {line_num}: {current_line.strip()}"

    def hunt_url(self, url):
        """Main hunting function for a single URL"""
        print(f"Hunting keywords in: {url}")
        
        try:
            # Load page with Selenium to handle dynamic content
            self.driver.get(url)
            
            # Wait for page to load and execute JavaScript
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait a bit more for async JS to load
            time.sleep(3)
            
            # Get final page source after JS execution
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Search in HTML content
            html_matches = self.search_keywords(page_source, 'HTML', url)
            self.findings.extend(html_matches)
            
            # Extract and analyze JavaScript files
            js_urls = self.extract_js_urls(soup, url)
            
            for js_url in js_urls:
                print(f"  Analyzing JS: {js_url}")
                js_content = self.get_js_content(js_url)
                if js_content:
                    js_matches = self.search_keywords(js_content, 'JavaScript', js_url)
                    self.findings.extend(js_matches)
                    
        except Exception as e:
            print(f"Error hunting {url}: {e}")

    def output_findings(self):
        """Output findings to STDOUT"""
        if not self.findings:
            print("No keyword matches found.")
            return
            
        print(f"\n=== KEYWORD HUNTING RESULTS ===")
        print(f"Found {len(self.findings)} matches:\n")
        
        for finding in self.findings[:3]:  # Only show first 3 findings
            print(f"🎯 {finding['group']}")
            print(f"   Pattern: {finding['pattern']}")
            print(f"   Match: {finding['match']}")
            print(f"   Source: {finding['source_url']} ({finding['content_type']})")
            print(f"   Context: {finding['line_context'][:300]}")
            print()
            
        if len(self.findings) > 3:
            print(f"... and {len(self.findings) - 3} more matches (showing first 3 only)")
            print()

    def notify_discord(self):
        """Send findings to Discord via discord_notify"""
        if not self.findings:
            return
            
        webhook_url = self.config.get('discord_webhook_url')
        if not webhook_url or 'YOUR_WEBHOOK_URL' in webhook_url:
            print("Discord webhook not configured, skipping Discord notification")
            return
            
        # Prepare Discord message
        message = f"🔍 **Keyword Hunter Results** \n\n"
        message += f"Found {len(self.findings)} matches:\n\n"
        
        for finding in self.findings[:3]:  # Limit to first 3 findings
            message += f"**{finding['group']}**\n"
            message += f"• Match: `{finding['match'][:100]}...` \n"
            message += f"• Source: {finding['source_url']}\n"
            message += f"• Context: `{finding['line_context'][:300]}`\n"
            message += f"• Type: {finding['content_type']}\n\n"
            
        if len(self.findings) > 3:
            message += f"... and {len(self.findings) - 3} more matches\n"
        
        try:
            # Use discord-notify library
            notifier = Notifier(webhook_url)
            notifier.send(message, print_message=False)
            print("Discord notification sent successfully")
                
        except Exception as e:
            print(f"Error sending Discord notification: {e}")

    def cleanup(self):
        """Cleanup webdriver"""
        if self.driver:
            self.driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Hunt for regex keywords in web pages and JS files")
    parser.add_argument('-u', '--url', help='URL to analyze')
    parser.add_argument('-c', '--config', default='config.yaml', help='Config file path')
    
    args = parser.parse_args()
    
    # If config path is relative, make it relative to script directory
    if not os.path.isabs(args.config):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        args.config = os.path.join(script_dir, args.config)
    
    # Get URL from argument or stdin
    if args.url:
        url = args.url
    else:
        url = sys.stdin.read().strip()
        
    if not url:
        print("Error: No URL provided. Use -u parameter or pipe URL to stdin.")
        sys.exit(1)
        
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    hunter = KeywordHunter(args.config)
    
    try:
        hunter.setup_webdriver()
        hunter.hunt_url(url)
        hunter.output_findings()
        hunter.notify_discord()
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        hunter.cleanup()

if __name__ == '__main__':
    main()